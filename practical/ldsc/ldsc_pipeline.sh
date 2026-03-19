#!/usr/bin/env bash
set -euo pipefail

# Student-facing LDSC practical.
# Assumes the instructor has already created the prepared inputs with:
#   Rscript practical/ldsc/prepare_ldsc_data.R [--force]

LDSC_DIR="${LDSC_DIR:-/path/to/ldsc}"
COURSE_DIR="practical/ldsc/data/course"
REF_DIR="practical/ldsc/data/ref"
RESULTS_DIR="practical/ldsc/data/results"

INTELLIGENCE_INPUT="${COURSE_DIR}/intelligence_ctg.tsv.gz"
P_FACTOR_INPUT="${COURSE_DIR}/p_factor.tsv.gz"

if [[ ! -f "${LDSC_DIR}/munge_sumstats.py" || ! -f "${LDSC_DIR}/ldsc.py" ]]; then
  echo "Set LDSC_DIR to the directory containing munge_sumstats.py and ldsc.py" >&2
  exit 1
fi

for required_file in \
  "${INTELLIGENCE_INPUT}" \
  "${P_FACTOR_INPUT}" \
  "${REF_DIR}/w_hm3.snplist"; do
  if [[ ! -f "${required_file}" ]]; then
    echo "Missing required input: ${required_file}" >&2
    echo "Run: Rscript practical/ldsc/prepare_ldsc_data.R --force" >&2
    exit 1
  fi
done

mkdir -p "${RESULTS_DIR}"

python "${LDSC_DIR}/munge_sumstats.py" \
  --sumstats "${INTELLIGENCE_INPUT}" \
  --out "${RESULTS_DIR}/intelligence_ctg" \
  --merge-alleles "${REF_DIR}/w_hm3.snplist"

python "${LDSC_DIR}/munge_sumstats.py" \
  --sumstats "${P_FACTOR_INPUT}" \
  --out "${RESULTS_DIR}/p_factor" \
  --merge-alleles "${REF_DIR}/w_hm3.snplist"

python "${LDSC_DIR}/ldsc.py" \
  --h2 "${RESULTS_DIR}/intelligence_ctg.sumstats.gz" \
  --ref-ld-chr "${REF_DIR}/eur_w_ld_chr/" \
  --w-ld-chr "${REF_DIR}/weights_hm3_no_hla/weights.hm3_noMHC." \
  --out "${RESULTS_DIR}/intelligence_h2"

python "${LDSC_DIR}/ldsc.py" \
  --h2 "${RESULTS_DIR}/p_factor.sumstats.gz" \
  --ref-ld-chr "${REF_DIR}/eur_w_ld_chr/" \
  --w-ld-chr "${REF_DIR}/weights_hm3_no_hla/weights.hm3_noMHC." \
  --out "${RESULTS_DIR}/p_factor_h2"

python "${LDSC_DIR}/ldsc.py" \
  --rg "${RESULTS_DIR}/intelligence_ctg.sumstats.gz,${RESULTS_DIR}/p_factor.sumstats.gz" \
  --ref-ld-chr "${REF_DIR}/eur_w_ld_chr/" \
  --w-ld-chr "${REF_DIR}/weights_hm3_no_hla/weights.hm3_noMHC." \
  --out "${RESULTS_DIR}/intelligence_p_factor_rg"

grep -E "Total Observed scale h2|Intercept|Ratio" "${RESULTS_DIR}/intelligence_h2.log"
grep -E "Total Observed scale h2|Intercept|Ratio" "${RESULTS_DIR}/p_factor_h2.log"
grep -E "Genetic Correlation|Intercept|P:" "${RESULTS_DIR}/intelligence_p_factor_rg.log"
