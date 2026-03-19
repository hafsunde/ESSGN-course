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

looks_like_archive <- function(path) {
  grepl("\\.(zip|tgz|tar|tar\\.gz|tar\\.bz2|gz|bz2)$", basename(path), ignore.case = TRUE)
}

safe_unlink <- function(path) {
  if (file.exists(path) || dir.exists(path)) {
    unlink(path, recursive = TRUE, force = TRUE)
  }
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

download_with_fallback <- function(urls, destfile) {
  dir.create(dirname(destfile), recursive = TRUE, showWarnings = FALSE)
  options(timeout = max(600, getOption("timeout")))

  headers <- c(
    "User-Agent" = "Mozilla/5.0 (compatible; ESSGN-course/1.0)",
    "Accept" = "*/*"
  )

  for (url in urls) {
    message("Downloading ", basename(destfile), " from ", url)
    safe_unlink(destfile)

    ok <- tryCatch({
      utils::download.file(
        url,
        destfile,
        mode = "wb",
        quiet = FALSE,
        method = if (capabilities("libcurl")) "libcurl" else "auto",
        headers = headers
      )
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

copy_matching_files <- function(from_dir, to_dir, pattern = NULL, rename_basename = identity) {
  dir.create(to_dir, recursive = TRUE, showWarnings = FALSE)
  files <- list.files(from_dir, recursive = TRUE, full.names = TRUE, all.files = FALSE, no.. = TRUE)
  files <- files[file.info(files)$isdir %in% FALSE]

  if (!is.null(pattern)) {
    files <- files[grepl(pattern, basename(files))]
  }

  if (length(files) == 0) {
    stop("No files matched in ", from_dir)
  }

  target_names <- vapply(basename(files), rename_basename, character(1))
  if (anyDuplicated(target_names)) {
    stop("Staged files would collide in ", to_dir)
  }

  ok <- file.copy(files, file.path(to_dir, target_names), overwrite = TRUE)
  if (!all(ok)) {
    stop("Failed to stage some extracted files in ", to_dir)
  }

  invisible(file.path(to_dir, target_names))
}

assert_expected_chr_files <- function(dir, stem = "", suffixes, label) {
  expected <- unlist(lapply(1:22, function(chr) {
    file.path(dir, paste0(stem, chr, suffixes))
  }))

  missing <- expected[!file.exists(expected)]
  if (length(missing) > 0) {
    stop(
      "Missing expected files in ", label, " after extraction, for example ",
      basename(missing[[1]])
    )
  }
}

extract_archive_if_needed <- function(path, exdir) {
  safe_unlink(exdir)
  dir.create(exdir, recursive = TRUE, showWarnings = FALSE)

  lower <- tolower(basename(path))
  if (grepl("\\.zip$", lower)) {
    utils::unzip(path, exdir = exdir, overwrite = TRUE)
  } else if (grepl("\\.(tgz|tar|tar\\.gz|tar\\.bz2)$", lower)) {
    extract_tar_archive(path, exdir)
  } else if (grepl("\\.(gz|bz2)$", lower)) {
    out_name <- sub("\\.(gz|bz2)$", "", basename(path), ignore.case = TRUE)
    decompress_single_file(path, file.path(exdir, out_name))
  } else {
    file.copy(path, file.path(exdir, basename(path)), overwrite = TRUE)
  }

  invisible(exdir)
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

score_sumstats_candidate <- function(path, preferred_patterns = character()) {
  name <- tolower(basename(path))
  score <- 0

  if (grepl("\\.(txt|tsv|sumstats|ma)$", name)) score <- score + 5
  if (grepl("\\.(txt|tsv|sumstats|ma)\\.(gz|bz2)$", name)) score <- score + 5
  if (grepl("harmon|munge|readme|supp|metadata|example", name)) score <- score - 10
  if (grepl("chr[0-9xy]+", name)) score <- score - 5

  for (i in seq_along(preferred_patterns)) {
    if (grepl(preferred_patterns[[i]], name, perl = TRUE)) {
      score <- score + (50 - i)
    }
  }

  score
}

find_sumstats_file <- function(path, stage_dir, preferred_patterns = character()) {
  lower <- tolower(basename(path))
  if (!looks_like_archive(path) && grepl("\\.(txt|tsv|sumstats|ma)(\\.(gz|bz2))?$", lower)) {
    return(path)
  }

  extract_archive_if_needed(path, stage_dir)
  files <- list.files(stage_dir, recursive = TRUE, full.names = TRUE, all.files = FALSE, no.. = TRUE)
  files <- files[file.info(files)$isdir %in% FALSE]

  if (length(files) == 0) {
    stop("No files found after extracting ", basename(path))
  }

  candidate_mask <- grepl("\\.(txt|tsv|sumstats|ma)(\\.(gz|bz2))?$", files, ignore.case = TRUE)
  candidates <- files[candidate_mask]
  if (length(candidates) == 0) {
    stop("Could not identify a summary statistics table inside ", basename(path))
  }

  scores <- vapply(candidates, score_sumstats_candidate, numeric(1), preferred_patterns = preferred_patterns)
  candidates[[order(scores, decreasing = TRUE)[[1]]]]
}

standardize_sumstats <- function(df, trait_label, default_n) {
  snp_col <- pick_column(df, c("SNP", "RSID", "MarkerName", "SNPID", "rsid"))
  a1_col <- pick_column(df, c("A1", "Allele1", "EffectAllele", "EA", "ALT", "effect_allele"))
  a2_col <- pick_column(df, c("A2", "Allele2", "OtherAllele", "NEA", "REF", "other_allele"))
  p_col <- pick_column(df, c("P", "Pval", "PValue", "PVAL", "p_value", "pval"))
  n_col <- pick_column(df, c("N", "Neff", "TotalSampleSize", "SampleSize", "N_eff", "n_total"), required = FALSE)
  z_col <- pick_column(df, c("Z", "Zscore", "ZScore", "ZStat", "zscore", "ZSCORE"), required = FALSE)
  beta_col <- pick_column(df, c("BETA", "Beta", "Effect", "beta", "B"), required = FALSE)
  se_col <- pick_column(df, c("SE", "StdErr", "StandardError", "se", "SEbeta"), required = FALSE)
  or_col <- pick_column(df, c("OR", "OddsRatio", "odds_ratio"), required = FALSE)

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

trait_specs <- function(raw_sumstats_dir, course_dir) {
  list(
    intelligence = list(
      label = "intelligence",
      download = file.path(raw_sumstats_dir, "intelligence_sumstats.zip"),
      urls = c("https://vu.data.surf.nl/public.php/dav/files/9tgwxmO5yosQkmb/?accept=zip"),
      preferred_patterns = c("intelligence", "iq", "cognitive", "gwas", "sumstat"),
      default_n = 269867,
      output = file.path(course_dir, "intelligence_ctg.tsv.gz")
    ),
    p_factor = list(
      label = "p_factor",
      download = file.path(raw_sumstats_dir, "p_factor_sumstats"),
      urls = c("https://figshare.com/ndownloader/files/58731898"),
      preferred_patterns = c("p[_ -]?factor", "pfactor", "transdiagnostic", "sumstat", "gwas"),
      default_n = 272757,
      output = file.path(course_dir, "p_factor.tsv.gz")
    )
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

  hm3_archive <- file.path(raw_ref_dir, "w_hm3.snplist.gz")
  eur_archive <- file.path(raw_ref_dir, "1000G_Phase3_ldscores.tgz")
  weights_archive <- file.path(raw_ref_dir, "1000G_Phase3_weights_hm3_no_MHC.tgz")

  specs <- trait_specs(raw_sumstats_dir, course_dir)
  for (spec in specs) {
    if (force || !file.exists(spec$download)) {
      download_with_fallback(spec$urls, spec$download)
    }
  }

  if (force || !file.exists(hm3_archive)) {
    download_with_fallback(
      c(
        "https://zenodo.org/records/7773502/files/w_hm3.snplist.gz?download=1",
        "https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/w_hm3.snplist.bz2",
        "https://data.broadinstitute.org/alkesgroup/LDSCORE/w_hm3.snplist.bz2"
      ),
      hm3_archive
    )
  }

  if (force || !file.exists(eur_archive)) {
    download_with_fallback(
      c(
        "https://zenodo.org/records/10515792/files/1000G_Phase3_ldscores.tgz?download=1",
        "https://zenodo.org/records/7768714/files/1000G_Phase3_ldscores.tgz?download=1",
        "https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/eur_w_ld_chr.tar.bz2",
        "https://data.broadinstitute.org/alkesgroup/LDSCORE/eur_w_ld_chr.tar.bz2"
      ),
      eur_archive
    )
  }

  if (force || !file.exists(weights_archive)) {
    download_with_fallback(
      c(
        "https://zenodo.org/records/10515792/files/1000G_Phase3_weights_hm3_no_MHC.tgz?download=1",
        "https://zenodo.org/records/7768714/files/1000G_Phase3_weights_hm3_no_MHC.tgz?download=1",
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
    safe_unlink(tmp_extract)
    dir.create(tmp_extract, recursive = TRUE, showWarnings = FALSE)
    extract_tar_archive(eur_archive, tmp_extract)
    safe_unlink(eur_ref_dir)
    dir.create(eur_ref_dir, recursive = TRUE, showWarnings = FALSE)
    copy_matching_files(
      tmp_extract,
      eur_ref_dir,
      pattern = "\\.(l2\\.ldscore\\.gz|l2\\.M|l2\\.M_5_50)$",
      rename_basename = function(x) sub("^1000G\\.EUR\\.QC\\.", "", x)
    )
    assert_expected_chr_files(
      eur_ref_dir,
      suffixes = c(".l2.ldscore.gz", ".l2.M", ".l2.M_5_50"),
      label = eur_ref_dir
    )
  }

  weights_ref_dir <- file.path(ref_dir, "weights_hm3_no_hla")
  if (force || !dir.exists(weights_ref_dir) || length(list.files(weights_ref_dir)) == 0) {
    tmp_extract <- file.path(tempdir(), "ldsc_weights_extract")
    safe_unlink(tmp_extract)
    dir.create(tmp_extract, recursive = TRUE, showWarnings = FALSE)
    extract_tar_archive(weights_archive, tmp_extract)
    safe_unlink(weights_ref_dir)
    dir.create(weights_ref_dir, recursive = TRUE, showWarnings = FALSE)
    copy_matching_files(tmp_extract, weights_ref_dir, pattern = "^weights\\.hm3_noMHC\\.")
    assert_expected_chr_files(
      weights_ref_dir,
      stem = "weights.hm3_noMHC.",
      suffixes = ".l2.ldscore.gz",
      label = weights_ref_dir
    )
  }

  hm3 <- read.delim(hm3_path, header = FALSE, stringsAsFactors = FALSE)
  hm3_snps <- unique(as.character(hm3[[1]]))
  hm3_snps <- hm3_snps[grepl("^rs", hm3_snps, ignore.case = TRUE)]

  outputs <- list()
  for (trait_name in names(specs)) {
    spec <- specs[[trait_name]]
    stage_dir <- file.path(raw_sumstats_dir, paste0(trait_name, "_staged"))
    source_file <- find_sumstats_file(spec$download, stage_dir, spec$preferred_patterns)
    message("Using ", source_file, " for trait ", spec$label)
    df <- read_sumstats_table(source_file)
    std <- standardize_sumstats(df, trait_label = spec$label, default_n = spec$default_n)
    std <- std[std$SNP %in% hm3_snps, ]
    message(spec$label, ": retained ", format(nrow(std), big.mark = ","), " HapMap3 SNPs")
    write_tsv_gz(std, spec$output)
    outputs[[trait_name]] <- spec$output
  }

  message("Prepared files written to ", normalizePath(course_dir, winslash = "/", mustWork = TRUE))
  invisible(c(
    outputs,
    list(
      hm3 = hm3_path,
      eur_ld = eur_ref_dir,
      weights = weights_ref_dir
    )
  ))
}

args <- commandArgs(trailingOnly = TRUE)
force <- any(args %in% c("--force", "force"))

if (sys.nframe() == 0) {
  prepare_ldsc_data(force = force)
}
