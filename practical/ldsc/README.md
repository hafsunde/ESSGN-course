# LDSC Practical

This folder contains a small course workflow for running LD score regression (LDSC) on two prepared GWAS summary-statistics files: `intelligence` and `p_factor`.

The practical is organized around three scripts:

## What The Three Scripts Do

### `prepare_ldsc_data.R`
This script prepares the course inputs.

It:
- downloads or reuses the raw GWAS summary statistics
- downloads or reuses the LDSC reference resources
- finds the real summary-statistics table inside each raw download
- standardizes the GWAS columns into the schema required by the course
- restricts the data to HapMap3 SNPs
- writes the cleaned course-ready files into `practical/ldsc/data/course`

### `install_ldsc.sh`
This script installs LDSC locally for the course.

It:
- clones the Python 3 LDSC implementation from `CBIIT/ldsc` into `practical/ldsc/ldsc`
- creates a local virtual environment in `practical/ldsc/.venv/ldsc`
- installs the Python packages needed for this course workflow
- verifies that `munge_sumstats.py` and `ldsc.py` can run

The installer intentionally skips annotation-only dependencies such as `pybedtools`. That is fine for this course, because we only use `munge_sumstats.py`, `ldsc.py --h2`, and `ldsc.py --rg`.

### `ldsc_pipeline.sh`
This script runs the actual LDSC analysis.

It:
- munges the prepared course files into LDSC's `.sumstats.gz` format
- estimates observed-scale SNP heritability for `intelligence`
- estimates observed-scale SNP heritability for `p_factor`
- estimates the genetic correlation between the two traits
- prints the key summary lines from the LDSC log files

## When To Run Each Script

Run the scripts in this order:

1. `Rscript practical/ldsc/prepare_ldsc_data.R --force`
2. `bash practical/ldsc/install_ldsc.sh`
3. `bash practical/ldsc/ldsc_pipeline.sh`

The first command prepares the input data, the second installs LDSC locally, and the third runs the LDSC workflow.

## Expected Folder Structure

After a successful setup, the important parts of `practical/ldsc` should look like this:

```text
practical/ldsc/
  prepare_ldsc_data.R
  install_ldsc.sh
  ldsc_pipeline.sh
  ldsc/
  .venv/
    ldsc/
  data/
    raw/
    ref/
    course/
    results/
```

The subfolders are used as follows:

- `data/raw/`: raw downloaded GWAS files and archives
- `data/ref/`: LDSC reference files such as HapMap3 SNPs, LD scores, and regression weights
- `data/course/`: cleaned course-ready summary-statistics files
- `data/results/`: LDSC outputs produced by the pipeline
- `ldsc/`: the local checkout of the LDSC code used by the course
- `.venv/ldsc/`: the local Python environment used to run LDSC

## Expected Key Outputs

After the pipeline finishes, you should expect at least these output files in `practical/ldsc/data/results`:

- `intelligence_ctg.sumstats.gz`
- `p_factor.sumstats.gz`
- `intelligence_h2.log`
- `p_factor_h2.log`
- `intelligence_p_factor_rg.log`

The `.sumstats.gz` files are LDSC's munged inputs, and the `.log` files contain the heritability and genetic-correlation results you will interpret in the practical.
