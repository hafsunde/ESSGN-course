#!/usr/bin/env bash
set -euo pipefail

# Student-facing LDSC practical.
# Assumes the instructor has already created the prepared inputs with:
#   practical/ldsc/prepare_ldsc_data.R

LDSC_DIR="${LDSC_DIR:-/path/to/ldsc}"
COURSE_DIR="practical/ldsc/data/course"
REF_DIR="practical/ldsc/data/ref"
RESULTS_DIR="practical/ldsc/data/results"

mkdir -p "${RESULTS_DIR}"

python "${LDSC_DIR}/munge_sumstats.py" \
  --sumstats "${COURSE_DIR}/intelligence_ctg.tsv.gz" \
  --out "${RESULTS_DIR}/intelligence_ctg" \
  --merge-alleles "${REF_DIR}/w_hm3.snplist"

python "${LDSC_DIR}/munge_sumstats.py" \
  --sumstats "${COURSE_DIR}/depression_ctg.tsv.gz" \
  --out "${RESULTS_DIR}/depression_ctg" \
  --merge-alleles "${REF_DIR}/w_hm3.snplist"

python "${LDSC_DIR}/ldsc.py" \
  --h2 "${RESULTS_DIR}/intelligence_ctg.sumstats.gz" \
  --ref-ld-chr "${REF_DIR}/eur_w_ld_chr/" \
  --w-ld-chr "${REF_DIR}/weights_hm3_no_hla/weights.hm3_noMHC." \
  --out "${RESULTS_DIR}/intelligence_h2"

python "${LDSC_DIR}/ldsc.py" \
  --h2 "${RESULTS_DIR}/depression_ctg.sumstats.gz" \
  --ref-ld-chr "${REF_DIR}/eur_w_ld_chr/" \
  --w-ld-chr "${REF_DIR}/weights_hm3_no_hla/weights.hm3_noMHC." \
  --out "${RESULTS_DIR}/depression_h2"

python "${LDSC_DIR}/ldsc.py" \
  --rg "${RESULTS_DIR}/intelligence_ctg.sumstats.gz,${RESULTS_DIR}/depression_ctg.sumstats.gz" \
  --ref-ld-chr "${REF_DIR}/eur_w_ld_chr/" \
  --w-ld-chr "${REF_DIR}/weights_hm3_no_hla/weights.hm3_noMHC." \
  --out "${RESULTS_DIR}/intelligence_depression_rg"

grep -E "Total Observed scale h2|Intercept|Ratio" "${RESULTS_DIR}/intelligence_h2.log"
grep -E "Total Observed scale h2|Intercept|Ratio" "${RESULTS_DIR}/depression_h2.log"
grep -E "Genetic Correlation|Intercept|P:" "${RESULTS_DIR}/intelligence_depression_rg.log"
