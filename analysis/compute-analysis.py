#!/usr/bin/env python3
"""RQ1/RQ3 analysis (Nov 18, 2026).

Inputs: the verified per-project 6-build match counts recorded in the study
design document section 5 (all counts verified from build-record.json hashes
during measurement; boot-ui counts from its full 6-build matrix).

Definitions:
- within-env match: the two builds inside one environment agree (E1 pair used;
  all three environments agreed on every project's within-env count).
- cross-env match: E1 build-1 vs E3 build-1 agree (AMD64 vs ARM64, the
  widest environment contrast; E1-vs-E2 equals E1-vs-E3 on every project).
- project fully reproducible: every artifact matches between every pair.
- boot-ui confound artifacts: the 19 scm-url artifacts (disclosed harness
  artifact; see design doc section 5). McNemar is reported with and without
  them.

Outputs: printed summary + analysis-results.json
"""
import json, math, os

# project: (n_artifacts, within_matches, cross_matches, fully_reproducible)
PROJECTS = {
    # pilot (5)
    "graphql-jpa-query":      (14, 0, 0, False),
    "ScheduleDashboard":      (2, 0, 0, False),
    "shopping-app-backend":   (1, 0, 0, False),
    "spring-ai-agentcore":    (11, 11, 11, True),
    "josdk-spring-boot-starter": (5, 0, 0, False),
    # phase 1 (20)
    "algafood-api-algaworks": (1, 0, 0, False),
    "Fintech-Payment-Processing-API": (1, 0, 0, False),
    "linguamate-agent":       (1, 0, 0, False),
    "detectionSystem":        (1, 0, 0, False),
    "PetsUniverseSpringBoot": (1, 0, 0, False),
    "dapr/java-sdk":          (17, 0, 0, False),
    "amqp-10-jms-spring-boot": (8, 2, 2, False),
    "datasource-micrometer":  (4, 0, 0, False),
    "book-manager":           (1, 0, 0, False),
    "zlm-spring-boot-starter": (1, 0, 0, False),
    "SpringVulnBoot-backend": (1, 0, 0, False),
    "SpringMVC-migration":    (1, 0, 0, False),
    "spring-boot-practice":   (1, 0, 0, False),
    "boot-ui":                (2895, 2818, 2781, False),
    "desafio-itau-backend":   (1, 0, 0, False),
    "chaos-monkey-spring-boot": (9, 0, 0, False),
    "spring-petclinic-data-jdbc": (1, 0, 0, False),
    "apollo":                 (12, 0, 0, False),
    "social-network":         (1, 0, 0, False),
    "trello-main":            (1, 0, 0, False),
}

def wilson(k, n, z=1.959964):
    if n == 0: return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z*z/n
    c = p + z*z/(2*n)
    m = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (max(0.0, (c-m)/d), min(1.0, (c+m)/d))

def mcnemar_exact(b, c):
    # two-sided exact binomial test on the discordant pairs
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k+1)) / 2**n
    return min(1.0, 2*p)

n_proj = len(PROJECTS)
n_full = sum(1 for v in PROJECTS.values() if v[3])
tot = sum(v[0] for v in PROJECTS.values())
within = sum(v[1] for v in PROJECTS.values())
cross = sum(v[2] for v in PROJECTS.values())
# discordant cells (artifact level): within-match/cross-mismatch = b,
# within-mismatch/cross-match = c. Only boot-ui contributes discordance:
# 19 artifacts match within but not cross (the scm-url confound); none match
# cross but not within (verified in the boot-ui matrix: E1-vs-E3 differing
# set = 77 within-diff + 19 cross-only; the 77 differ both ways).
# Paired comparison on the 2,877 paths common to E1 and E3; the 18 arch-only
# brotli paths per side have no counterpart and are not pairs. The 18
# generated-bytecode jars found post-fix are inside the 77: they differed
# within-environment in the baseline (timestamps) and only became cross-only
# differences after the fix normalized timestamps.
b_all, c_all = 19, 0
# excluding the 19 confound artifacts:
b_ex, c_ex = 0, 0
# excluding boot-ui entirely:
tot_nb = tot - 2895; within_nb = within - 2818; cross_nb = cross - 2781

out = {
    "projects": n_proj,
    "fully_reproducible_projects": n_full,
    "project_rate": n_full / n_proj,
    "project_rate_wilson95": wilson(n_full, n_proj),
    "artifacts_per_build": tot,
    "within_env_matches": within,
    "within_env_rate": within / tot,
    "within_env_wilson95": wilson(within, tot),
    "cross_env_matches": cross,
    "cross_env_rate": cross / tot,
    "cross_env_wilson95": wilson(cross, tot),
    "mcnemar_all": {"b_within_only": b_all, "c_cross_only": c_all, "p_exact_two_sided": mcnemar_exact(b_all, c_all)},
    "mcnemar_excl_confound": {"b_within_only": b_ex, "c_cross_only": c_ex, "p_exact_two_sided": mcnemar_exact(b_ex, c_ex)},
    "excl_boot_ui": {
        "artifacts": tot_nb, "within_matches": within_nb, "cross_matches": cross_nb,
        "within_rate": within_nb / tot_nb, "cross_rate": cross_nb / tot_nb,
        "within_wilson95": wilson(within_nb, tot_nb), "cross_wilson95": wilson(cross_nb, tot_nb),
    },
    "fix_phase": {
        "mismatching_projects": 24,
        "fully_fixed_all_six_builds": 23,
        "fixed_with_disclosed_residuals": 1,
        "step2_only_one_iteration": 20,  # 3 pilot + 17 phase-1
        "multi_attempt": ["ScheduleDashboard (3, step 2)", "spring-petclinic-data-jdbc (3, steps 2+6)",
                          "apollo (2, steps 2+6)", "boot-ui (3, step 2)"],
    },
}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis-results.json"), "w"), indent=1)
