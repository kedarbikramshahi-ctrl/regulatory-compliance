# Project B — live source-access report

Assigned business review date: **26 August 2026**. Access checks performed: **11 October 2026**. All times below are UTC, not the assigned review date. 23:04 UTC corresponds to 7:04 PM America/New_York on this date.

## Latest follow-up result

The three previously unresolved legal documents are now readable through the documented official Cellar API, with identity/version mappings verified. **POLICY remains unresolved.** The initial results below are preserved as history; see the follow-up section at the end for current statuses, alternative URLs, timestamps, and transport/version limitations. No legal conclusions are made.

## Initial result and scope

Ten distinct sources were disclosed in the original stakeholder export, interviews/project-b-regulatory-compliance-20261011-2051.md. Repeated disclosures of EVIDENCE and CALENDAR refer to the same URLs and are counted once.

Fresh read-only attempts obtained readable document content from six routes: SYSTEMS, EVIDENCE, CALENDAR, LAW, TIME, and FAQ. POLICY returned only a JavaScript application shell. OJ, AMEND, and CONSOLIDATED returned a generic Official Journal landing page rather than the requested document. HTTP 200 alone is not retrieval success.

No credentials were entered, transmitted, or printed. No company records were changed. No fictional fixtures or local substitutes were used as live evidence. No legal applicability, compliance, or approval conclusion was made. Only this access report was created; no workflow, snapshots, final compliance drafts, source archive, Git commit, or push was implemented.

This report establishes access observations, not a completed assessment source bundle. The material was inspected in memory; assessment-ready captured bytes/extracts and fine-grained locators still need a future authorized capture workflow.

## Attempt methods and limitations

1. Fresh web-tool opens of all ten exact disclosed URLs ran between 2026-10-11T23:02:57Z and 2026-10-11T23:02:59Z. The tool could not open the four company URLs. LAW, TIME, and FAQ returned relevant content. All three EUR-Lex attempts returned a JavaScript/robot-check response. Tool caching behavior is not independently controlled or verified.
2. A read-only browser retry could not proceed: no browser surfaces were available, and the in-app browser was unavailable. No CAPTCHA was solved or access restriction bypassed.
3. Fresh direct HTTP GETs were then sent to all ten exact URLs, with Cache-Control: no-cache and Pragma: no-cache. The individual request start/completion times appear below. No authentication headers, cookies, or credentials were supplied. These headers request revalidation but do not prove that an upstream cache was bypassed.
4. Relevant web-page metadata was inspected for LAW and FAQ. Availability today and suitability as of 26 August 2026 are distinct checks. No historical copy, publication history, or independently verified legal revision chain was obtained.

## Company sources

### POLICY — internal policies

Exact disclosed URL: [https://private-pecorino-70e.notion.site/Project-2-Regulatory-Compliance-Current-Internal-Policies-3ba0b700541e81f09998d48f3b1c2856](https://private-pecorino-70e.notion.site/Project-2-Regulatory-Compliance-Current-Internal-Policies-3ba0b700541e81f09998d48f3b1c2856)

- Retrieval: **requested policy content not obtained; unverified response**. HTTP 200, text/html; charset=utf-8, 20,056 characters.
- Actual request start: 2026-10-11T23:04:14.7156911Z. Completion: 2026-10-11T23:04:15.7604700Z.
- Returned identity: generic Notion page; response requests JavaScript. The policy title, policy clauses, owners, version, and effective dates were not readable.
- Version: **unverified**. The URL's descriptive slug is not proof of document identity/version.
- Suitability for 26 August 2026: **cannot determine** until the actual policy and its revision/effective-date information are read.
- Authentication/access problem: web tool could not access this route; direct GET returned only the application shell. This does not prove that sign-in is required or that access is denied. Need a supported JavaScript browser through the intended route; if it then prompts for authentication or permissions, report that separately.

### SYSTEMS — AI system register

Exact disclosed URL: [https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU](https://docs.google.com/spreadsheets/d/10ky745H_1h9XbGCXPJsiRp5yfdeU08TZtmrsCMinGgU)

- Retrieval: **succeeded for readable register content**. HTTP 200, text/html; charset=utf-8, 256,094 characters.
- Actual request start: 2026-10-11T23:04:15.9603236Z. Completion: 2026-10-11T23:04:18.4992356Z.
- Returned identity: Project B — AI System Register, with table headers including system_id, actor-role fields, use_case, evidence_updated_at, and record_version. Real rows were present in the returned document; this was not just a login screen.
- Version: observed row-level record_version values include register-2026-08-26. This is a source-provided business version label, not an independently verified Google revision ID or immutable historical snapshot.
- Suitability for 26 August 2026: **provisionally relevant**, because the displayed business version matches the assigned date. Full row/revision inspection and actual date/meaning checks are still needed before treating every record as suitable historical evidence.
- Authentication/access problem: no authentication was needed to read the returned table. HTML includes a Sign in control and JavaScript/browser-support warnings, but those did not prevent returned table content. Initial web-tool retrieval failed; direct HTTP access succeeded. Edit access was not tested or requested.

### EVIDENCE — incident and evidence register

Exact disclosed URL: [https://docs.google.com/spreadsheets/d/19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk](https://docs.google.com/spreadsheets/d/19BYZ68OSbsa1i9OfF6MzthrdC6q6mt6IWk6ucI8u7Rk)

- Retrieval: **succeeded for readable register content**. HTTP 200, text/html; charset=utf-8, 250,267 characters.
- Actual request start: 2026-10-11T23:04:18.5206048Z. Completion: 2026-10-11T23:04:21.0269180Z.
- Returned identity: Project B — Incident and Evidence Register. Table headers include record_id, system_id, record_type, reported_at, owner, status, evidence_ref, evidence_state, and notes.
- Version: **no explicit register revision was verified in the inspected content**. Individual report dates and evidence-reference labels are present; neither is a whole-document revision identifier. An evidence_ref is not proof the referenced screenshot, SOP, or incident attachment was retrieved.
- Suitability for 26 August 2026: **relevant candidate, historical suitability unconfirmed**. Observed sample rows have report dates on/before the assigned date, but complete row/revision checks and referenced-evidence access are still needed. Missing, stale, or conflicting row states are business findings to retain, not an HTTP retrieval failure.
- Authentication/access problem: readable table content without credentials; web-tool access failed. JavaScript warnings and a Sign in control appear in the HTML but do not establish an authentication requirement for the returned rows. No referenced attachment was retrieved in this access check.

### CALENDAR — compliance calendar

Exact disclosed URL: [https://docs.google.com/spreadsheets/d/1xtXl_P7Yb9LaECZjjgtlyI-idoAJTAhH-1gQ4vQaCGA](https://docs.google.com/spreadsheets/d/1xtXl_P7Yb9LaECZjjgtlyI-idoAJTAhH-1gQ4vQaCGA)

- Retrieval: **succeeded for readable calendar-register content**. HTTP 200, text/html; charset=utf-8, 252,412 characters.
- Actual request start: 2026-10-11T23:04:21.0269180Z. Completion: 2026-10-11T23:04:23.2888479Z.
- Returned identity: Project B — Compliance Calendar. Table headers include action_id, system_id, action, owner, due_date, status, approval_required, and source_version.
- Version: observed source_version values include calendar-2026-08-26. This business label is not an independently verified immutable Google revision.
- Suitability for 26 August 2026: **provisionally relevant**, subject to revision and date-meaning confirmation. Dates later than the review date may be planned tasks; their existence alone does not make the source unsuitable. No due date is treated as human-approved merely because it appears in this register.
- Authentication/access problem: table readable without credentials. Initial web-tool retrieval failed; direct HTTP succeeded with JavaScript warnings and a Sign in control. No production calendar was written, and no task/status/date was changed.

## Official legal, timing, and guidance routes

### LAW — Article 50 service-desk page

Exact disclosed URL: [https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50)

- Retrieval: **succeeded**. HTTP 200, text/html; charset=utf-8, 89,445 characters. Web tool also returned readable Article 50 content.
- Actual direct request start: 2026-10-11T23:04:23.2898484Z. Completion: 2026-10-11T23:04:24.0431601Z.
- Returned identity: Article 50 service-desk page, with explanatory summary and numbered article paragraphs. The summary is identified as non-binding on the page.
- Version: its About this text section identifies a consolidated-text basis dated 27 July 2026 and amendment markers. This is the page's own description; the underlying consolidated and amending documents were not independently retrieved successfully.
- Suitability for 26 August 2026: **provisionally date-aligned reference**, but not sufficient to verify the required primary-authority/version chain. A pre-review basis date does not alone prove the complete applicable text as of the assigned date. No legal applicability finding is made.
- Authentication/access problem: none encountered for this page. No credential entry or sign-in required.

### OJ — requested original regulation

Exact disclosed URL: [https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng)

- Retrieval: **failed to obtain the requested regulation; invalid/unsuitable response for the intended source**. HTTP 200, text/html, 13,692 characters.
- Actual direct request start: 2026-10-11T23:04:24.0443940Z. Completion: 2026-10-11T23:04:24.4088500Z.
- Requested identity from locator: original Regulation (EU) 2024/1689. Returned identity: generic EUR-Lex Official Journal listing, showing October 2026 issue dates, rather than the regulation's text/title/version.
- Version: **requested regulation version not verified**. Do not infer it from the URL alone.
- Suitability for 26 August 2026: **returned page is unsuitable as evidence of the requested original regulation**. The original route may still be usable through a supported access method; no claim is made that the regulation itself is unavailable everywhere.
- Authentication/access problem: web-tool attempt returned a JavaScript robot-verification page. Direct GET returned an OJ landing page. No login requirement was established. Browser retry unavailable; challenge was not solved or bypassed.

### AMEND — requested amending Official Journal item

Exact disclosed URL: [https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ%3AL_202601744](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ%3AL_202601744)

- Retrieval: **failed to obtain the requested item; invalid/unsuitable response for the intended source**. HTTP 200, text/html, 13,692 characters.
- Actual direct request start: 2026-10-11T23:04:24.4098501Z. Completion: 2026-10-11T23:04:24.6605378Z.
- Requested locator: OJ:L_202601744, disclosed as AMEND. Returned identity: generic Official Journal listing, not the requested act. The act's actual title, publication date, effect, and relation to Article 50 remain unverified.
- Version: **unverified**. The source label and URL identifier do not establish an amending instrument's actual content.
- Suitability for 26 August 2026: **cannot evaluate the intended act**; the returned landing page is unsuitable. Do not substitute the service-desk description for retrieval of this primary source.
- Authentication/access problem: web tool returned JavaScript/robot verification; direct GET returned the OJ landing page. No credential prompt or confirmed access entitlement issue was observed.

### CONSOLIDATED — requested dated consolidated text

Exact disclosed URL: [https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727)

- Retrieval: **failed to obtain the requested consolidated text; invalid/unsuitable response**. HTTP 200, text/html, 13,692 characters.
- Actual direct request start: 2026-10-11T23:04:24.6800443Z. Completion: 2026-10-11T23:04:24.9719441Z.
- Requested identity/version encoded in locator: consolidated Regulation 2024/1689 as at 27 July 2026. Returned identity: generic Official Journal listing. The web tool also observed redirection to TodayOJ/index.html with the CELEX query and then robot verification.
- Version: **not verified from the requested document**. The date in the locator and the LAW page's description are not substitutes for the actual consolidated text.
- Suitability for 26 August 2026: **intended date is a relevant candidate, but document suitability cannot be confirmed** because its text/version was not obtained. The returned OJ listing is not suitable legal evidence.
- Authentication/access problem: JavaScript/robot-check and landing-page responses; browser unavailable. No login was attempted or CAPTCHA bypassed.

### TIME — implementation timeline

Exact disclosed URL: [https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline)

- Retrieval: **succeeded**. HTTP 200, text/html; charset=utf-8, 36,225 characters. Web tool also obtained relevant content.
- Actual direct request start: 2026-10-11T23:04:24.9719441Z. Completion: 2026-10-11T23:04:25.4515103Z.
- Returned identity: official AI Act implementation timeline. The current page states that it incorporates Digital Omnibus amendments and presents dated implementation milestones.
- Version: **no explicit page revision/publication date was verified** in the inspected content. Milestone dates are not publication or retrieval dates.
- Suitability for 26 August 2026: **useful timing context, historical suitability unconfirmed**. Current amended timeline content must be reconciled with the successfully verified legal text/version before being used for an as-of timing conclusion. No deadline or applicability conclusion is drawn here.
- Authentication/access problem: none encountered; readable without credentials.

### FAQ — Article 50 transparency FAQ

Exact disclosed URL: [https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act)

- Retrieval: **succeeded**. HTTP 200, text/html; charset=UTF-8, 75,761 characters. Web tool also obtained readable FAQ content.
- Actual direct request start: 2026-10-11T23:04:25.4525304Z. Completion: 2026-10-11T23:04:25.8083931Z.
- Returned identity: Commission Article 50 transparency FAQ, presented as explanatory material related to Commission guidelines.
- Version: visible Last update metadata: **24 July 2026**. This is page-provided metadata, not an immutable historical archive or verified legal version.
- Suitability for 26 August 2026: **provisionally suitable explanatory context**, based on the reported pre-review update date. Historical immutability is not established. It does not replace binding text or determine legal interpretation.
- Authentication/access problem: none encountered; readable without credentials.

## Access follow-up needed

- POLICY: open the exact disclosed route in an available supported JavaScript browser and verify the policy content/version; ask the facilitator about access if that route prompts for sign-in or remains unavailable.
- OJ, AMEND, CONSOLIDATED: establish an intended route that returns each actual requested act/version. Retain these failed/unsuitable observations in any later live workflow rather than marking HTTP 200 as success or replacing them with fictional/local data. Ask the facilitator to verify the disclosed locators and permitted access route if failures persist.
- Company registers: confirm that the displayed business version labels and row dates correspond to the intended as-of facts. EVIDENCE revision and referenced attachment access need separate checks; authentication has not been shown to be a blocker for the tables themselves.
- TIME/LAW/FAQ: preserve source-role distinctions and verify historical suitability against primary sources. This report does not certify the review's legal authority chain.

The live-source access gate is therefore **partially successful**. Three company registers are readable, but the policy and the three requested EUR-Lex legal documents remain unresolved. No formal legal conclusions should be inferred from this access report.


## Follow-up verification — four previously unresolved routes

Follow-up date: 11 October 2026. Times are UTC. Original disclosures and the initial failed observations above are retained as history; the findings below supersede their current access status.

### Latest status

| Source | Current content-access result | Identity/version verified | Suitability for 26 August 2026 |
|---|---|---|---|
| POLICY | Unresolved | Actual policy title, clauses, revision/effective dates not obtained | Cannot assess until authorized readable policy is obtained |
| OJ | Retrieved through official Cellar API, despite original-route failure | CELEX 32024R1689; Regulation 2024/1689 dated 13 June 2024; OJ publication 12 July 2024; English original-publication rendition | Suitable original-source baseline for the review; not a substitute for considering later amendments |
| AMEND | Retrieved through official Cellar API, despite original-route failure | CELEX 32026R1744; Regulation 2026/1744 dated 8 July 2026; OJ publication 24 July 2026; English original-publication rendition | Relevant pre-review amending source; system-level applicability and provision-specific timing remain for subsequent review |
| CONSOLIDATED | Retrieved via alternate official EUR-Lex link and Cellar API | CELEX 02024R1689-20260727; English consolidation dated 27 July 2026; revision 001.001 | Date-aligned consolidation for investigation; completeness of the as-of amendment/correction chain is not certified |

This is document identity and date-suitability verification, not a final legal interpretation. The consolidation identifies itself as a documentation aid; do not treat it as a replacement for the authentic original and amending publications. No newer-revision search or full legal reconciliation was performed.

### POLICY: exact failure and permitted alternatives

Original route, unchanged:

https://private-pecorino-70e.notion.site/Project-2-Regulatory-Compliance-Current-Internal-Policies-3ba0b700541e81f09998d48f3b1c2856

The fresh GET again returned HTTP 200 with a generic Notion title and a JavaScript-required shell, not policy content. This proves that static HTML retrieval did not expose the policy, not that the policy is nonexistent or that a human user's browser is forbidden.

A documented read-only Notion API route was tested with the page ID derived from the disclosed URL:

https://api.notion.com/v1/pages/3ba0b700-541e-81f0-9998-d48f3b1c2856

It returned **HTTP 401 Unauthorized**. The request supplied a supported Notion-Version header but no credential. No token was searched for, supplied, guessed, or exposed, and no authenticated retry was made. Official [Notion page API documentation](https://developers.notion.com/reference/retrieve-a-page) requires bearer authentication and read-content capability; retrieving metadata alone also does not retrieve the policy body. Body content requires the documented block-children read, with authorization and pagination. A candidate content endpoint, documented but **not called after the 401**, is:

https://api.notion.com/v1/blocks/3ba0b700-541e-81f0-9998-d48f3b1c2856/children

Browser inventory again returned no available browser. No automated export API, undocumented internal Notion endpoint, credential extraction, login bypass, or access-control bypass was attempted. No visible public download link was available in the shell, so no fabricated download URL was claimed.

Required assistance: the facilitator/source owner should confirm the exact policy route and historical revision, and provide access through an available normal JavaScript browser, or an already authorized Notion integration with read access to that page. If they authorize a source export, record its provenance/version and permitted route explicitly; do not silently substitute a local copy for the required live attempt. Credentials should never be pasted into this report or committed.

### EUR-Lex: exact failures and legitimate alternatives

The original OJ, AMEND, and CONSOLIDATED URLs are unchanged in the earlier sections. Fresh direct requests on this pass returned **HTTP 202, text/html, with an empty body**, including direct PDF/HTML variants. No document or PDF bytes were obtained from those responses. Prior web-tool attempts returned robot/JavaScript challenges or the OJ landing page. These are distinct observed response failures; an underlying server-side cause is not established. No challenge was solved or bypassed.

Public format URLs tested are listed in the attempt log below. These are normal official document-format routes, not instructions to evade a challenge. The indexed official English consolidation link below returned readable content through the web tool:

https://eur-lex.europa.eu/legal-content/en/TXT/?qid=1790822129312&uri=CELEX%3A02024R1689-20260727

The returned document has a version header identifying 02024R1689, English, 27 July 2026, revision 001.001, and includes Article 50. It references the original act and the 2026/1744 amendment. The qid parameter was retained from an official indexed result; it is a search-context parameter, not an authentication credential. The web tool's upstream cache behavior is unverified. Following the embedded original/amending/PDF links still returned challenge or landing pages, so those unsuccessful attempts were not counted as content retrieval.

A separate **documented public Cellar dissemination API** then succeeded, with no authentication. Request headers selected metadata or the English XHTML rendition:

- Metadata: Accept: application/xml;notice=tree
- Content: Accept: application/xhtml+xml
- Language: Accept-Language: eng

Official [Publications Office Cellar documentation](https://op.europa.eu/en/web/cellar/cellar-data/publications) describes this content-negotiation mechanism. This is an authorized public retrieval service distinct from EUR-Lex's challenge page; no security tokens or challenge-response mechanisms were used. The EUR-Lex SOAP search service requires registration and approved credentials and does not directly download document files, according to its [official service guidance](https://eur-lex.europa.eu/content/help/data-reuse/webservice.html?locale=en). No account registration or authenticated SOAP request was attempted.

### Verified Cellar mappings, identity, and versions

**OJ**

Alternate request URL: https://publications.europa.eu/resource/celex/32024R1689

The XML metadata explicitly maps CELEX 32024R1689, OJ L_202401689, and the original ELI reg/2024/1689/oj to the same Cellar work. The English XHTML identifies Regulation (EU) 2024/1689, dated 13 June 2024, laying down harmonised rules on artificial intelligence, with OJ header dated 12 July 2024. Its rendition title is L_202401689EN.000101.fmx.xml; Article 50 is present. It is the original-publication rendition, not the July 2026 consolidation. An HTML converter generation timestamp is not an act's adoption/publication/effective date.

Resolved content URL returned by the service:

http://publications.europa.eu/resource/cellar/dc8116a1-3fe6-11ef-865a-01aa75ed71a1.0006.03/DOC_1

Resolved XML metadata URL:

http://publications.europa.eu/resource/cellar/dc8116a1-3fe6-11ef-865a-01aa75ed71a1/xml/tree?decoding=en

**AMEND**

Alternate request URL: https://publications.europa.eu/resource/celex/32026R1744

XML metadata explicitly maps CELEX 32026R1744, OJ L_202601744, and ELI reg/2026/1744/oj. The XHTML identifies Regulation (EU) 2026/1744, dated 8 July 2026, amending regulations including 2024/1689 for simplification of AI-rule implementation (Digital Omnibus on AI). The OJ header is dated 24 July 2026; rendition title L_202601744EN.000101.fmx.xml. The body includes Article 50 references. This establishes the intended act's identity and pre-review publication, not a final conclusion about any system's obligations.

Resolved content URL:

http://publications.europa.eu/resource/cellar/b459c07f-86fb-11f1-bf5e-01aa75ed71a1.0006.03/DOC_1

Resolved XML metadata URL:

http://publications.europa.eu/resource/cellar/b459c07f-86fb-11f1-bf5e-01aa75ed71a1/xml/tree?decoding=en

**CONSOLIDATED**

Alternate request URL: https://publications.europa.eu/resource/celex/02024R1689-20260727

XML metadata maps CELEX 02024R1689-20260727 to the consolidation 2024R1689/20260727 and dated ELI reg/2024/1689/2026-07-27. English content identifies consolidation date 27 July 2026 and revision 001.001, and includes Article 50 and the original/amendment relationships. Its documentation-only disclaimer is retained as a source-role limitation.

Resolved content URL:

http://publications.europa.eu/resource/cellar/b1730fb2-8f1c-11f1-9262-01aa75ed71a1.0001.03/DOC_1

Resolved XML metadata URL:

http://publications.europa.eu/resource/cellar/b1730fb2-8f1c-11f1-9262-01aa75ed71a1/xml/tree?decoding=en

All Cellar requests started with HTTPS, but the service returned HTTP content/metadata redirect URLs as shown above. No browser certificate warning was bypassed and no sensitive data was transmitted. This report records the transport limitation rather than claiming authenticated signatures or cryptographic proof of authenticity. The requested PDFs were not obtained or signature-validated. A later assessment-ready capture should preserve actual response bytes and hashes and, if required, verify an authenticated OJ PDF or a secure official rendition. Hashes alone do not authenticate an act.

### Fresh direct-request attempt log

All date/time entries below are on 2026-10-11 and use UTC. Direct-request precision is rounded here to milliseconds; the attempts are separate from the business review date. Blank body does not mean successful retrieval.

| Source/method | Exact request URL | Start → finish UTC | Response/result |
|---|---|---|---|
| POLICY original | https://private-pecorino-70e.notion.site/Project-2-Regulatory-Compliance-Current-Internal-Policies-3ba0b700541e81f09998d48f3b1c2856 | 23:10:05.694 → 23:10:06.383 | 200; Notion JavaScript shell, no policy content |
| POLICY official API | https://api.notion.com/v1/pages/3ba0b700-541e-81f0-9998-d48f3b1c2856 | 23:10:06.495 → 23:10:06.759 | 401 Unauthorized; stopped without credentials |
| OJ original | https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng | 23:10:06.769 → 23:10:06.894 | 202; empty HTML response |
| OJ PDF | https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A32024R1689 | 23:10:06.894 → 23:10:06.928 | 202; no PDF/content |
| OJ HTML | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A32024R1689 | 23:10:06.928 → 23:10:06.954 | 202; empty HTML |
| AMEND original | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ%3AL_202601744 | 23:10:06.955 → 23:10:06.981 | 202; empty HTML |
| AMEND ELI PDF | https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng/pdf | 23:10:06.981 → 23:10:06.995 | 202; no PDF/content |
| AMEND HTML | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A32026R1744 | 23:10:06.995 → 23:10:07.028 | 202; empty HTML |
| CONSOLIDATED original | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727 | 23:10:07.028 → 23:10:07.050 | 202; empty HTML |
| CONSOLIDATED PDF | https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A02024R1689-20260727 | 23:10:07.051 → 23:10:07.076 | 202; no PDF/content |
| CONSOLIDATED HTML | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02024R1689-20260727 | 23:10:07.076 → 23:10:07.095 | 202; empty HTML |
| CONSOLIDATED ELI PDF | https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng/pdf | 23:10:07.095 → 23:10:07.155 | 202; no PDF/content |
| OJ Cellar XML | https://publications.europa.eu/resource/celex/32024R1689 | 23:11:31.428 → 23:11:33.562 | 200; XML metadata including CELEX/OJ/ELI mapping |
| OJ Cellar XHTML | https://publications.europa.eu/resource/celex/32024R1689 | 23:11:33.663 → 23:11:35.463 | 200; readable English act, 1,257,134 characters |
| AMEND Cellar XML | https://publications.europa.eu/resource/celex/32026R1744 | 23:11:35.463 → 23:11:37.214 | 200; XML CELEX/OJ/ELI mapping |
| AMEND Cellar XHTML | https://publications.europa.eu/resource/celex/32026R1744 | Individual start/finish not retained in displayed output; bounded by preceding XML completion and following request start | 200; English act; full identity rechecked below |
| CONSOLIDATED Cellar XML | https://publications.europa.eu/resource/celex/02024R1689-20260727 | 23:11:37.963 → 23:11:38.896 | 200; XML consolidation/CELEX/ELI mapping |
| CONSOLIDATED Cellar XHTML | https://publications.europa.eu/resource/celex/02024R1689-20260727 | 23:11:38.896 → 23:11:40.239 | 200; English consolidation, 847,869 characters |
| OJ Cellar identity recheck | https://publications.europa.eu/resource/celex/32024R1689 | 23:12:19.498 → 23:12:21.970 | 200 XHTML; title/publication/Article 50 checked |
| AMEND Cellar identity recheck | https://publications.europa.eu/resource/celex/32026R1744 | 23:12:22.082 → 23:12:22.763 | 200 XHTML; title/publication/Article 50 references checked; 349,164 characters |
| CONSOLIDATED Cellar identity recheck | https://publications.europa.eu/resource/celex/02024R1689-20260727 | 23:12:22.763 → 23:12:24.150 | 200 XHTML; dated revision/relationships/Article 50 checked |

The same Cellar URL returned different representations based on the documented Accept header. Its XML response is metadata, not the act's body. Character counts are not byte counts or file hashes. No body was saved as an assessment artifact during this report-only task.

### Additional web-tool attempts retained

- Public OJ PDF: https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ%3AL_202401689 — robot/JavaScript challenge.
- Public AMEND PDF: https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ%3AL_202601744 — redirected to OJ landing page.
- Consolidated ELI PDF: https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng/pdf — robot/JavaScript challenge.
- Alternate English consolidated HTML: https://eur-lex.europa.eu/legal-content/en/TXT/?qid=1790822129312&uri=CELEX%3A02024R1689-20260727 — readable dated English document; completion observed at 23:10:21 UTC (individual request start not separately measured).
- AMEND text: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32026R1744 — no usable act returned by web tool.
- Cellar resource without representation negotiation: https://publications.europa.eu/resource/celex/32024R1689 — web-tool error; negotiated direct GET later succeeded.
- Embedded original link: https://eur-lex.europa.eu/legal-content/EN/AUTO/?uri=celex%3A32024R1689 — robot/JavaScript challenge.
- Embedded amendment link: https://eur-lex.europa.eu/legal-content/EN/AUTO/?uri=celex%3A32026R1744 — robot/JavaScript challenge.
- Embedded consolidated PDF: https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A02024R1689-20260727 — OJ landing page.

The three embedded-link attempts were observed between 23:10:49 and 23:10:51 UTC. Other initial web PDF attempts completed by 23:09:05 UTC; individual per-link times were not measured. Search snippets were used only to discover official alternatives, not to establish document identity. Search-context and percent-decoding redirects are not silently substituted for original routes.

### Remaining assistance and boundaries

**POLICY remains unresolved.** Obtain authorized readable content and verified revision/effective dates via its intended route, with facilitator/source-owner assistance. Do not use fictional policy data or an unverified copied policy.

**The three legal documents are now content-accessible through official public alternatives.** Keep the original-route failures in the attempt history. The identified versions predate the assigned review date, but this access test does not certify the absence of additional applicable changes, the full historical chain, PDF signature authenticity, or any system's legal status. Those are later verification tasks.

Only source-access-report.md is updated. No company mutation, permission change, account creation, CAPTCHA solving, credential use, full-workflow implementation, legal conclusion, commit, or push occurred. The other six sources were not retested on this focused follow-up.
