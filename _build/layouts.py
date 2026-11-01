# How each project page arranges its images around the text (live-site structure: lead image(s) -> text -> the rest).
# lead:  rows shown above the text.          rows: rows shown after the text.
# side:  an image placed beside the text (text left, image right); "split" keeps the first N paragraphs above it.
# wide:  with side, give the image the larger share of the width.
# masonry: remaining images in N columns instead of rows.   strip: stacked full-height infographic slices.
LAYOUTS = {
  # diagrams
  "data-analysis-framework": dict(side="terraflow.webp", wide=True),
  "safety-instrumented-systems": dict(lead=[["sis-architectures.webp"]],
      rows=[["sis-stages.webp", "sis-1oo2.webp"], ["sis-elements.webp", "sis-signal.webp"], ["sis-valve-open.webp", "sis-valve-closed.webp"]]),
  "atoms-in-optical-tweezers": dict(lead=[["atoms-laser_rev1.webp"]],
      rows=[["atoms-laser_basic.webp", "atoms-laser_var1.webp", "atoms-laser_var2.webp"]]),
  "geology-diagrams": dict(lead=[["geo-map.webp"]], rows=[["geo-interp.webp"], ["geo-logs.webp", "geo-cm.webp"]]),
  "constitutional-ai-training-diagram": dict(strip=True),
  "introduction-to-effective-altruism-infographic": dict(strip=True),
  "molecular-neuroscience-processes": dict(lead=[["nlrp3-activation.webp"]], rows=[["drp1-nlrp3.webp"]]),
  # comics
  "young-and-old-genes": dict(lead=[["genes-young-old.webp"]], side="genes-young-old-color-sketch.webp", split=3),
  "noisy-genes": dict(lead=[["genes-network2.webp"]]),
  "faults-errors-failures": dict(lead=[["safety1.webp"]], rows=[["safety2.webp", "safety5.webp"], ["safety6.webp"]]),
  "seismic-monitoring": dict(lead=[["k-utec-alerting.webp"]], side="k-utec-applications.webp"),
  "spacetime": dict(lead=[["spacetime1.webp"]],
      rows=[["spacetime2.webp", "spacetime3.webp"], ["spacetime4.webp", "spacetime5.webp"], ["spacetime6.webp", "spacetime8.webp"], ["spacetime9.webp", "spacetime7.webp"]]),
  "bad-bug-busters": dict(side="BBB-eBook-Cover.webp",
      rows=[["bbb6.webp"], ["bbb7.webp"], ["bbb10.webp", "bbb12.webp"], ["bbb9-2.webp", "bbb11.webp"]]),
  "the-honest-microbes": dict(lead=[["teeth12.webp", "teeth13.webp"]],
      rows=[["teeth0.webp", "teeth1.webp", "teeth3.webp", "teeth6.webp"], ["teeth8.webp", "teeth9.webp", "teeth10.webp", "teeth16.webp"]]),
  "brett-the-beaker": dict(lead=[["brett7.webp", "brett9.webp"]],
      rows=[["brett1.webp", "brett6.webp", "brett4.webp"], ["brett10.webp", "brett14.webp", "brett15.webp"]]),
  "sealife-poems": dict(lead=[["octopus2.webp", "mussel2.webp"]], masonry=3),
  "neuron-synapses": dict(side="neurons-exercise.webp", wide=True),
  "the-adventures-of-rosie-frankenshmirtz": dict(lead=[["aorf11.webp", "aorf6.webp"]],
      rows=[["aorf1.webp", "aorf7.webp"], ["aorf4.webp", "aorf3.webp"], ["aorf10.webp", "aorf12.webp"], ["aorf13.webp", "aorf8.webp"]]),
  "radiomon": dict(lead=[["kalium.webp", "plumbum.webp"]],
      rows=[["aurum.webp", "argentum.webp", "cobalt.webp", "bismuth.webp"], ["helium.webp", "neon.webp", "ferrum.webp", "carbon.webp"]]),
}

# One line under each project title: what the project is, in practice (max 10 words, fewer is better).
SUBS = {
  "data-analysis-framework": "Workflow diagram for a cytometry startup",
  "safety-instrumented-systems": "Technical figures for a functional safety paper",
  "atoms-in-optical-tweezers": "Figure for a quantum computing paper",
  "geology-diagrams": "Maps and figures for a hydrogeology paper",
  "constitutional-ai-training-diagram": "Explainer diagram of an AI training method",
  "introduction-to-effective-altruism-infographic": "Infographic version of an introductory article",
  "molecular-neuroscience-processes": "Figures for an Alzheimer's research paper",
  "young-and-old-genes": "Illustration of an evolutionary genetics study",
  "noisy-genes": "Illustration of a gene expression study",
  "faults-errors-failures": "Illustrations for a functional safety paper",
  "seismic-monitoring": "Explainers for a seismic monitoring service",
  "spacetime": "Storyboard for animated physics videos",
  "bad-bug-busters": "Children's picture book about vaccines",
  "the-honest-microbes": "Children's book about dental hygiene",
  "brett-the-beaker": "Children's book about lab equipment",
  "sealife-poems": "Children's book of sea life poems",
  "neuron-synapses": "Illustration of an exercise and brain study",
  "the-adventures-of-rosie-frankenshmirtz": "Children's book about a space mission",
  "radiomon": "Characters for a nuclear physics game",
}

# Topic tags for the filters on the Diagrams and Comics pages (keys -> labels in TAG_LABELS, in pill order).
TAG_LABELS = {
  "biology": "Biology", "health": "Health & medicine", "physics": "Physics", "chemistry": "Chemistry",
  "space": "Space", "earth": "Earth science", "engineering": "Engineering", "ai": "AI",
  "ea": "Effective altruism", "kids": "Children's books",
}
TAGS = {
  "data-analysis-framework": ["biology", "health"],
  "safety-instrumented-systems": ["engineering"],
  "atoms-in-optical-tweezers": ["physics"],
  "geology-diagrams": ["earth"],
  "constitutional-ai-training-diagram": ["ai"],
  "introduction-to-effective-altruism-infographic": ["ea"],
  "molecular-neuroscience-processes": ["biology", "health"],
  "aml-research-program": ["biology", "health"],
  "young-and-old-genes": ["biology"],
  "noisy-genes": ["biology"],
  "faults-errors-failures": ["engineering"],
  "seismic-monitoring": ["engineering", "earth"],
  "spacetime": ["physics", "space"],
  "bad-bug-busters": ["health", "biology", "kids"],
  "the-honest-microbes": ["health", "biology", "kids"],
  "brett-the-beaker": ["chemistry", "kids"],
  "sealife-poems": ["biology", "kids"],
  "neuron-synapses": ["biology", "health"],
  "the-adventures-of-rosie-frankenshmirtz": ["space", "kids"],
  "radiomon": ["physics", "chemistry"],
}
