# Senzing Bootcamp Plugin Feedback

Feedback that arrived **by email** rather than through `/senzing-bootcamp:bootcamp-feedback`, captured
here so it has a content-addressed ledger identity like any other entry. The **What happened** section
below is the sender's message **verbatim** — it has not been paraphrased, corrected, or reordered.
Everything outside that section is triage metadata added by the maintainer flow.

**Captured:** 2026-08-21
**Channel:** email, relayed to the maintainer by the sender
**Relationship to the archived files:** the same bootcamper filed
`feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK_1787320390.md` (7 entries, processed 2026-08-21). This is
a later, separate report and is not among those entries.

## Improvement: the ER output loaded into a graph database shows nodes with no edges and none of the AML attributes

**Date:** 2026-08-21
**Module:** Query, Visualize and Discover / graduation (post-mapping output)
**Priority:** pending
**Source:** bootcamper-reported
**Routing:** plugin — the bootcamp captures `integration_targets` and never produces an artifact shaped for them; the sender's stated cause (an un-enforced "Enrichment" step) names a step the bootcamp does not have
**Upstream:** not applicable

### What happened

Verbatim, as sent:

> I believe the Enrichment steps in the bootcamp wasn't enforced. Reason – as I load the Senzing ER
> output into Neo4j DB and GDS (in my other machine, we are using Memgraph + MAGE as equivalent to
> Neo4j and GDS); yet, the output only show bubbles without any network and relationship, and upon
> checking the output file, for some reason the mule accounts, off-ramps, dormant account, from
> sender to target, amounts, are not there. In case I'm wrong, you may want to check the final steps
> of the bootcamp at the post mapping.
>
> Here's the final output which is more AML use case specific now based on the sample datasets which
> I've generated (for this UI/UX, I'm using Kinevix/GraphXR, similar to Neo4j Bloom), and by going
> back to Senzing to run the Enrichment steps: (I've put this in a pptx meant for c-suite with
> business focus benefits highlighted).

### Why it matters

The bootcamper's own words carry it: the ER output, loaded into the graph platform they intend to use
it in, rendered as disconnected nodes with none of the business attributes their use case is about.
They then obtained a usable result by working outside the bootcamp and presented it to a C-suite
audience — so the bootcamp's final artifact was not the one that did the job.

### Suggested fix

The bootcamper's suggestion is to check the final steps of the bootcamp at the post-mapping stage.
They attribute the gap to "the Enrichment steps" not being enforced.

### Context when reported

- **Time:** 2026-08-21 (report); the bootcamp run it refers to was 2026-08-18
- **Plugin version:** 0.5.1 for the run being described (per the sender's earlier entries)
- **Workstation:** macOS 24.4.0 (Intel x86_64) for the bootcamp run; a second machine for the graph
  database work
- **Downstream stack:** Neo4j + GDS as the intended target; Memgraph + MAGE used as the equivalent on
  the second machine; Kinevix/GraphXR for the UI/UX (described as similar to Neo4j Bloom)
- **Module / step:** not stated — the sender points at "the final steps of the bootcamp at the post
  mapping"
- **Observed problem:** nodes render with no edges ("bubbles without any network and relationship");
  the output file lacks mule-account, off-ramp, dormant-account, sender-to-target and amount data
- **Expected behavior:** an output that carries entities, the relationships between them, and the
  business attributes the AML use case is built on
- **Attachment referenced but not received:** a pptx containing the working final output. It defines
  what the sender considers a correct result and was not available at triage time.
- **Premise to check before acting:** the sender's diagnosis names an "Enrichment" step. Whether the
  bootcamp has one is a question for triage, not an assumption to carry forward.
