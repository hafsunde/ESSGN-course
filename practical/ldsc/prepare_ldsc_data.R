get_script_path <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    return(normalizePath(sub("^--file=", "", file_arg[[1]]), winslash = "/", mustWork = FALSE))
  }

  frame_file <- tryCatch(sys.frames()[[1]]$ofile, error = function(...) NULL)
  if (!is.null(frame_file)) {
    return(normalizePath(frame_file, winslash = "/", mustWork = FALSE))
  }

  normalizePath(file.path("practical", "ldsc", "prepare_ldsc_data.R"),
    winslash = "/",
    mustWork = FALSE
  )
}

normalize_names <- function(x) {
  tolower(gsub("[^a-z0-9]+", "", x))
}

pick_column <- function(df, aliases, required = TRUE) {
  nm <- normalize_names(names(df))
  hits <- which(nm %in% normalize_names(aliases))
  if (length(hits) > 0) {
    return(names(df)[hits[[1]]])
  }

  if (required) {
    stop("Could not find any of these columns: ", paste(aliases, collapse = ", "))
  }

  NULL
}

download_with_fallback <- function(urls, destfile) {
  dir.create(dirname(destfile), recursive = TRUE, showWarnings = FALSE)

  for (url in urls) {
    message("Downloading ", basename(destfile), " from ", url)
    ok <- tryCatch({
      utils::download.file(url, destfile, mode = "wb", quiet = FALSE)
      TRUE
    }, error = function(e) {
      message("  failed: ", conditionMessage(e))
      FALSE
    })

    if (ok && file.exists(destfile) && file.info(destfile)$size > 0) {
      return(invisible(destfile))
    }
  }

  stop("All download attempts failed for ", basename(destfile))
}

extract_tar_archive <- function(archive, exdir) {
  dir.create(exdir, recursive = TRUE, showWarnings = FALSE)
  status <- system2("tar", c("-xf", normalizePath(archive, winslash = "/", mustWork = TRUE), "-C", normalizePath(exdir, winslash = "/", mustWork = TRUE)))
  if (!identical(status, 0L)) {
    stop("Extraction failed for ", archive)
  }
}

decompress_single_file <- function(src, destfile) {
  dir.create(dirname(destfile), recursive = TRUE, showWarnings = FALSE)

  in_con <- if (grepl("\\.bz2$", src, ignore.case = TRUE)) {
    bzfile(src, open = "rb")
  } else if (grepl("\\.gz$", src, ignore.case = TRUE)) {
    gzfile(src, open = "rb")
  } else {
    file(src, open = "rb")
  }

  on.exit(close(in_con), add = TRUE)

  out_con <- file(destfile, open = "wb")
  on.exit(close(out_con), add = TRUE)

  repeat {
    chunk <- readBin(in_con, what = raw(), n = 1024 * 1024)
    if (length(chunk) == 0) {
      break
    }
    writeBin(chunk, out_con)
  }

  invisible(destfile)
}

copy_matching_files <- function(from_dir, to_dir, pattern = NULL) {
  dir.create(to_dir, recursive = TRUE, showWarnings = FALSE)
  files <- list.files(from_dir, recursive = TRUE, full.names = TRUE, all.files = FALSE, no.. = TRUE)
  files <- files[file.info(files)$isdir %in% FALSE]

  if (!is.null(pattern)) {
    files <- files[grepl(pattern, basename(files))]
  }

  if (length(files) == 0) {
    stop("No files matched in ", from_dir)
  }

  ok <- file.copy(files, file.path(to_dir, basename(files)), overwrite = TRUE)
  if (!all(ok)) {
    stop("Failed to stage some extracted files in ", to_dir)
  }

  invisible(file.path(to_dir, basename(files)))
}

read_sumstats_table <- function(path) {
  if (requireNamespace("data.table", quietly = TRUE)) {
    return(data.table::fread(path, data.table = FALSE, showProgress = TRUE))
  }

  utils::read.delim(path,
    header = TRUE,
    sep = "\t",
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
}

standardize_sumstats <- function(df, trait_label, default_n) {
  snp_col <- pick_column(df, c("SNP", "RSID", "MarkerName", "SNPID"))
  a1_col <- pick_column(df, c("A1", "Allele1", "EffectAllele", "EA"))
  a2_col <- pick_column(df, c("A2", "Allele2", "OtherAllele", "NEA"))
  p_col <- pick_column(df, c("P", "Pval", "PValue", "PVAL"))
  n_col <- pick_column(df, c("N", "Neff", "TotalSampleSize", "SampleSize"), required = FALSE)
  z_col <- pick_column(df, c("Z", "Zscore", "ZScore", "ZStat"), required = FALSE)
  beta_col <- pick_column(df, c("BETA", "Beta", "Effect"), required = FALSE)
  se_col <- pick_column(df, c("SE", "StdErr", "StandardError"), required = FALSE)
  or_col <- pick_column(df, c("OR", "OddsRatio"), required = FALSE)

  out <- data.frame(
    SNP = as.character(df[[snp_col]]),
    A1 = toupper(as.character(df[[a1_col]])),
    A2 = toupper(as.character(df[[a2_col]])),
    P = suppressWarnings(as.numeric(df[[p_col]])),
    stringsAsFactors = FALSE
  )

  if (!is.null(n_col)) {
    out$N <- suppressWarnings(as.numeric(df[[n_col]]))
  } else {
    out$N <- default_n
  }

  if (!is.null(z_col)) {
    out$Z <- suppressWarnings(as.numeric(df[[z_col]]))
  } else if (!is.null(beta_col) && !is.null(se_col)) {
    out$Z <- suppressWarnings(as.numeric(df[[beta_col]]) / as.numeric(df[[se_col]]))
  } else if (!is.null(or_col) && !is.null(se_col)) {
    out$Z <- suppressWarnings(log(as.numeric(df[[or_col]])) / as.numeric(df[[se_col]]))
  } else {
    stop("Could not construct Z for ", trait_label, ". Need Z, or BETA/SE, or OR/SE.")
  }

  keep <- !is.na(out$P) &
    !is.na(out$N) &
    !is.na(out$Z) &
    nzchar(out$SNP) &
    nzchar(out$A1) &
    nzchar(out$A2) &
    out$P > 0 &
    out$P <= 1 &
    out$N > 0 &
    grepl("^rs", out$SNP, ignore.case = TRUE) &
    nchar(out$A1) == 1 &
    nchar(out$A2) == 1 &
    out$A1 %in% c("A", "C", "G", "T") &
    out$A2 %in% c("A", "C", "G", "T") &
    out$A1 != out$A2

  out <- out[keep, c("SNP", "A1", "A2", "P", "N", "Z")]
  out <- out[!duplicated(out$SNP), ]

  message(trait_label, ": retained ", format(nrow(out), big.mark = ","), " rows after standardization")
  out
}

write_tsv_gz <- function(df, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  con <- gzfile(path, open = "wt")
  on.exit(close(con), add = TRUE)
  utils::write.table(df, con,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE,
    col.names = TRUE
  )
}

prepare_ldsc_data <- function(force = FALSE) {
  script_dir <- dirname(get_script_path())
  ldsc_dir <- normalizePath(script_dir, winslash = "/", mustWork = TRUE)

  raw_dir <- file.path(ldsc_dir, "data", "raw")
  raw_sumstats_dir <- file.path(raw_dir, "sumstats")
  raw_ref_dir <- file.path(raw_dir, "ref")
  ref_dir <- file.path(ldsc_dir, "data", "ref")
  course_dir <- file.path(ldsc_dir, "data", "course")

  dir.create(raw_sumstats_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(raw_ref_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(ref_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(course_dir, recursive = TRUE, showWarnings = FALSE)

  intelligence_zip <- file.path(raw_sumstats_dir, "SavageJansen_IntMeta_sumstats.zip")
  depression_gz <- file.path(raw_sumstats_dir, "sumstats_depression_ctg_format.txt.gz")
  hm3_archive <- file.path(raw_ref_dir, "w_hm3.snplist.bz2")
  eur_archive <- file.path(raw_ref_dir, "eur_w_ld_chr.tar.bz2")
  weights_archive <- file.path(raw_ref_dir, "1000G_Phase3_weights_hm3_no_MHC.tgz")

  if (force || !file.exists(intelligence_zip)) {
    download_with_fallback(
      c(
        "https://ctg.cncr.nl/documents/p1651/SavageJansen_IntMeta_sumstats.zip"
      ),
      intelligence_zip
    )
  }

  if (force || !file.exists(depression_gz)) {
    download_with_fallback(
      c(
        "https://ctg.cncr.nl/documents/p1651/sumstats_depression_ctg_format.txt.gz"
      ),
      depression_gz
    )
  }

  if (force || !file.exists(hm3_archive)) {
    download_with_fallback(
      c(
        "https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/w_hm3.snplist.bz2",
        "https://data.broadinstitute.org/alkesgroup/LDSCORE/w_hm3.snplist.bz2"
      ),
      hm3_archive
    )
  }

  if (force || !file.exists(eur_archive)) {
    download_with_fallback(
      c(
        "https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/eur_w_ld_chr.tar.bz2",
        "https://data.broadinstitute.org/alkesgroup/LDSCORE/eur_w_ld_chr.tar.bz2"
      ),
      eur_archive
    )
  }

  if (force || !file.exists(weights_archive)) {
    download_with_fallback(
      c(
        "https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/1000G_Phase3_weights_hm3_no_MHC.tgz",
        "https://data.broadinstitute.org/alkesgroup/LDSCORE/1000G_Phase3_weights_hm3_no_MHC.tgz"
      ),
      weights_archive
    )
  }

  hm3_path <- file.path(ref_dir, "w_hm3.snplist")
  if (force || !file.exists(hm3_path)) {
    decompress_single_file(hm3_archive, hm3_path)
  }

  eur_ref_dir <- file.path(ref_dir, "eur_w_ld_chr")
  if (force || !dir.exists(eur_ref_dir) || length(list.files(eur_ref_dir)) == 0) {
    tmp_extract <- file.path(tempdir(), "ldsc_eur_extract")
    unlink(tmp_extract, recursive = TRUE, force = TRUE)
    dir.create(tmp_extract, recursive = TRUE, showWarnings = FALSE)
    extract_tar_archive(eur_archive, tmp_extract)
    unlink(eur_ref_dir, recursive = TRUE, force = TRUE)
    dir.create(eur_ref_dir, recursive = TRUE, showWarnings = FALSE)
    copy_matching_files(tmp_extract, eur_ref_dir)
  }

  weights_ref_dir <- file.path(ref_dir, "weights_hm3_no_hla")
  if (force || !dir.exists(weights_ref_dir) || length(list.files(weights_ref_dir)) == 0) {
    tmp_extract <- file.path(tempdir(), "ldsc_weights_extract")
    unlink(tmp_extract, recursive = TRUE, force = TRUE)
    dir.create(tmp_extract, recursive = TRUE, showWarnings = FALSE)
    extract_tar_archive(weights_archive, tmp_extract)
    unlink(weights_ref_dir, recursive = TRUE, force = TRUE)
    dir.create(weights_ref_dir, recursive = TRUE, showWarnings = FALSE)
    copy_matching_files(tmp_extract, weights_ref_dir, pattern = "^weights\\.hm3_noMHC\\.")
  }

  hm3 <- read.delim(hm3_path, stringsAsFactors = FALSE)
  hm3_snps <- unique(as.character(hm3[[1]]))

  intelligence_stage <- file.path(raw_sumstats_dir, "intelligence_unzipped")
  dir.create(intelligence_stage, recursive = TRUE, showWarnings = FALSE)
  unzip(intelligence_zip, exdir = intelligence_stage, overwrite = TRUE)
  intelligence_candidates <- list.files(intelligence_stage,
    pattern = "\\.(txt|tsv|sumstats)$",
    recursive = TRUE,
    full.names = TRUE,
    ignore.case = TRUE
  )

  if (length(intelligence_candidates) == 0) {
    stop("Could not find the extracted intelligence summary statistics file")
  }

  intelligence_df <- read_sumstats_table(intelligence_candidates[[1]])
  depression_df <- read_sumstats_table(depression_gz)

  intelligence_std <- standardize_sumstats(
    intelligence_df,
    trait_label = "intelligence",
    default_n = 269867
  )
  depression_std <- standardize_sumstats(
    depression_df,
    trait_label = "depression",
    default_n = 449484
  )

  intelligence_std <- intelligence_std[intelligence_std$SNP %in% hm3_snps, ]
  depression_std <- depression_std[depression_std$SNP %in% hm3_snps, ]

  message("intelligence: retained ", format(nrow(intelligence_std), big.mark = ","), " HapMap3 SNPs")
  message("depression: retained ", format(nrow(depression_std), big.mark = ","), " HapMap3 SNPs")

  write_tsv_gz(intelligence_std, file.path(course_dir, "intelligence_ctg.tsv.gz"))
  write_tsv_gz(depression_std, file.path(course_dir, "depression_ctg.tsv.gz"))

  message("Prepared files written to ", normalizePath(course_dir, winslash = "/", mustWork = TRUE))
  invisible(list(
    intelligence = file.path(course_dir, "intelligence_ctg.tsv.gz"),
    depression = file.path(course_dir, "depression_ctg.tsv.gz"),
    hm3 = hm3_path,
    eur_ld = eur_ref_dir,
    weights = weights_ref_dir
  ))
}

if (sys.nframe() == 0) {
  prepare_ldsc_data()
}
