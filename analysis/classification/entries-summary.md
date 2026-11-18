# Entry-level classification (within-E1 pairs)

Raw codes from `classify-entries.py` on within-E1 build-1/build-2 JAR pairs:
entry membership, entry order, per-entry SHA-256, and per-entry zip
timestamps. MIXED pairs (an embedded JAR differing) were resolved by
recursive inspection of the embedded JAR; see the classification summary
for the resolved causes. The 4 pilot projects are covered in
`pilot-diffs/CLASSIFICATION.md`, not here.

| Project | Pairs | IDENTICAL | TIMESTAMP_ONLY | ORDERING | MIXED |
|---|---:|---:|---:|---:|---:|
| luanferreiradev/algafood-api-algaworks | 1 | 0 | 1 | 0 | 0 |
| Pawan-Ghode/Fintech-Payment-Processing-API | 1 | 0 | 1 | 0 | 0 |
| Coelho-Techne/detectionSystem | 1 | 0 | 1 | 0 | 0 |
| bulangya-bu/linguamate-agent | 1 | 0 | 1 | 0 | 0 |
| Thissvane/PetsUniverseSpringBoot | 1 | 0 | 1 | 0 | 0 |
| amqphub/amqp-10-jms-spring-boot | 8 | 2 | 6 | 0 | 0 |
| dapr/java-sdk | 17 | 0 | 16 | 0 | 1 |
| codecentric/spring-boot-admin (excluded project, not in sample) | 2 | 2 | 0 | 0 | 0 |
| HQfire/book-manager | 1 | 0 | 1 | 0 | 0 |
| jdbc-observations/datasource-micrometer | 4 | 0 | 4 | 0 | 0 |
| diva154/SpringMVC-to-SpringBoot-CRUDoperation-Migration | 1 | 0 | 1 | 0 | 0 |
| bansh2eBreak/SpringVulnBoot-backend | 1 | 0 | 1 | 0 | 0 |
| lunasaw/zlm-spring-boot-starter | 1 | 0 | 1 | 0 | 0 |
| penpencil721-lab/spring-boot-practice | 1 | 0 | 1 | 0 | 0 |
| codecentric/chaos-monkey-spring-boot | 9 | 0 | 4 | 0 | 5 |
| JoseOtavioJunqueira/desafio-itau-backend | 1 | 0 | 1 | 0 | 0 |
| apolloconfig/apollo | 12 | 0 | 0 | 0 | 12 |
| spring-petclinic/spring-petclinic-data-jdbc | 1 | 0 | 0 | 0 | 1 |
| thangtranitwork/social-network | 1 | 0 | 1 | 0 | 0 |
| Temirlan222/trello-main | 1 | 0 | 1 | 0 | 0 |
