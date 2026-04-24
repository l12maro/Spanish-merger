---
title: "Replication of Study 'The social meaning of a merger: The evaluation of an Andalusian Spanish consonant merger (ceceo)' by Regan (2022, Language in Society)"
author: "Lorena Martin Rodriguez (lmaro@stanford.edu)"
date: ""
format:
  html:
    toc: true
    toc_depth: 3
---

## Introduction

Regan (2022) explored the social evaluations associated with the Andalusian Spanish dialectal feature of _ceceo_ and its counterpart, _distinción_. While standard Spanish uses _distinción_, the pronunciation of sounds [s̪] and [θ] as two different phonemes, _ceceo_ refers to the merger of both sounds as [θ], which occurs is certain areas of Andalusian Spanish. The author employed a matched-guise experiment using twelve Western Andalusian speakers to explore the social evaluations associated with both _distinción_ and _ceceo_. Participants listened to speech that included different pronunciation of [s̪] and [θ] in syllable-initial position and evaluated them based on social status, urban vs rural, professions and formality, amongst other factors. The results found that speakers of _distinción_ were evaluated as being of higher social status, urban and more formal than those of _ceceo_.

However, the study did not include another form of fricative merger in Spanish, _seseo_. _Seseo_ refers to the merger of the sounds [s̪] and [θ] as [s̪]. Like _ceceo_, this merger is a dialectal variation found in Andalusian dialect. The current replication aims to analyze the social evaluations of both dialectal mergers, _ceceo_ and _seseo_. Since dialectal areas of _seseo_ include large urban areas within Andalusia, it is hypothesized that _seseo_ will be associated with higher social status and more urban and more formal than _ceceo_, even in areas where _ceceo_ is the dominant dialectal feature.

## Methods

### Planned Sample

Expected sample size consists of 100 to 200 listeners. The listeners should be nationals of Spain who are native speakers of Peninsular Spanish. The study will control for place of residence to ensure a balanced sample between urban and rural participants as well as speakers of both dialects.

### Materials

The original study extracted its stimuli from informal sociolinguistic interviews that have been conducted by the author. In the current replication, the stimuli is generated following the criteria of inclusion used in the original experiment. The stimuli contains data from at least two speakers, a female spaker and a male speaker.

### Procedure	

"The guises were uploaded and organized into an online survey using Qualtrics (2005–2020). The two guises (ceceo, distinción) for each of the twelve speakers were divided into two separate surveys balanced by variant and speaker gender/origin (see box B in the appendix). Following Barnes (Reference Barnes2015), these two versions were branched so that each participant would be randomly assigned to one version. Consequently, listeners heard each voice only once. Splitting the experiment into two surveys reduced the time of completion and avoided voice recognition given each speaker's unique utterance.

There were twelve distractors from twelve additional speakers placed into each version, balanced by speaker gender/origin. The distractors did not include syllable-initial coronal fricatives. Each version of the survey was pseudo-randomized to ensure that listeners did not hear several ceceo or distinción guises back-to-back.

Upon consenting to the terms of the study, participants were told that they would hear two to five second recordings from twenty-four different speakers (see box C in the appendix). They were permitted to listen to each recording as many times as they chose and then had to respond to a series of questions. They were asked to wear headphones and listen to the recordings in a quiet place. After hearing each recording, the listeners had to rate each speaker on nine different questions (see box D in the appendix). The first six questions were a set of social characteristics based on a six-point Likert scale; an even number was implemented to avoid neutral responses following previous studies (Campbell-Kibler Reference Campbell-Kibler2007; Walker, García, Cortés, & Campbell-Kibler Reference Walker, García, Cortés and Campbell-Kibler2014; Barnes Reference Barnes2015; Chappell Reference Chappell2016, Reference Chappell2018). For these social characteristics (only English scripts are provided here), they were asked ‘This persons sounds…’: (i) ‘of low socioeconomic level’/‘of high socioeconomic level’; (ii) ‘with less studies’/‘with more studies’; (iii) ‘less masculine’/‘more masculine’ for male voices and ‘more feminine’/‘less feminine’ for female voices; (iv) ‘less friendly’/‘more friendly’; (v) ‘more rural’/‘more urban’; and (vi) ‘informal’/‘formal’. There were also three multiple-choice questions. The first question of perceived occupation included: ‘works in a bar/restaurant’, ‘works in construction’, ‘works in a store’, ‘works in the field’, ‘is an administrator’, ‘is a teacher’, ‘is a doctor/lawyer’. The second question of perceived age included: < 30, 30–40, 40–50, 50–60, > 60. Finally, perceived origin included: Huelva capital, Lepe, and otro sitio ‘another place’. These questions were based on the author's participant observations and previous production findings in the region (Regan Reference Regan2017b, Reference Regan2020). Finally, after completing all twenty-four evaluations (twelve guises, twelve distractors), participants then answered basic demographic questions about themselves." (Reagan, 2022: 492), see modifications in section "Differences from original study".

### Analysis Plan

"Following Barnes (Reference Barnes, 2015), perceived occupation was converted into a five-point scale based on occupational prestige scales in Spain (Carabaña Morales & Gómez Bueno Reference Carabaña Morales and Bueno1996) and perceived age was converted into a five-point scale. Given the discrepancy between five and six-point scales, all values were centered on zero. A principle component analysis using the princomp function was conducted in R (R Core Team 2019) with all eight continuous dependent measures to assess the potential number of underlying factors, followed by a factor analysis using the factanal function. The dependent measures of perceived friendliness, masculinity/femininity, and age received high uniqueness scores. They were analyzed independently and it was found that only masculinity/femininity demonstrated significant results in mixed effects linear regression models. Thus, perceived friendliness and perceived age were disregarded and a new primary component analysis and factor analysis were run with the remaining six dependent measures. Based on the Eigen values and a scree plot, it was determined that there were three underlying factors. The first factor was a combined ‘status’ factor, loading perceived socioeconomic level, education level, and occupational prestige. The second factor loaded perceived urban-ness and formality. However, there were several differences between measures that were missed when combining urban-ness and formality into a single factor, therefore resulting in these measures being analyzed separately. The third factor loaded only perceived masculinity/femininity, which was removed from further analysis as the best mixed effects model (i.e. lowest AIC) only included the main effect for speaker gender. Thus, there were a total of three continuous dependent measures: status, urban-ness, and formality.

For each of these dependent measures a separate mixed effects linear regression model was created using the lmer function (Bates, Maechler, Bolker, & Walker Reference Bates, Maechler, Bolker and Walker2015) and lmerTest (Kuznetsova, Brockhoff, & Christensen Reference Kuznetsova, Brockhoff and Christensen2014) in R with two random intercepts of speaker and participant (listener) as well as the random slope of variant by participant. The independent variables tested in the various models included: variant (ceceo, distinción), speaker gender (male, female), listener gender (male, female), listener origin (Huelva capital, Lepe), listener education (1–5), listener age (eighteen to sixty-seven), and listener years lived away from Huelva/Lepe (zero to thirty). Listener years away serves as a limited proxy for geographic mobility. Listener education is a five-point scale based on educational levels: primary (1), secondary (2), bachillerato/professional formation (3), undergraduate degree (4), and graduate degree (5). All independent variables were tested in model construction with each social factor in interaction with variant. Three-way interactions between variant by listener origin by other social factors were tested to examine differences between communities. Within each model, non-statistically significant interactions with variant were removed from subsequent models. Estimated marginal means (Lenth, Singmann, Love, Buerkner, & Herve Reference Lenth, Singmann, Love, Buerkner and Herve2018) were used to conduct post-hoc analyses for interactions with more than two categorical levels.

As perceived origin was a three-way categorical dependent variable (Huelva, Lepe, otro sitio), a separate multinomial logistic regression model was fitted to the listeners’ evaluations of speaker origin using the multinom function in the nnet package (Venables & Ripley Reference Venables and Ripley2002). Z-scores and p-values were calculated manually." (Reagan, 2022: 492), see modifications in section "Differences from original study"

### Differences from Original Study

#### Differences in stimuli
Stimuli will be recorded from six speakers instead of 12, balanced by gender. Speakers will not be from Huelva or Lepe, as in the original study, but from Almonte.

#### Differences in procedure
Speakers will be asked for perceived origin regarding region (i.e. Huelva, Sevilla, otro sitio) rather than location.

#### Differences in analysis
None

### Methods Addendum (Post Data Collection)

You can comment this section out prior to final report with data collection.

#### Actual Sample
  Sample size, demographics, data exclusions based on rules spelled out in analysis plan

#### Differences from pre-data collection methods plan
  Any differences from what was described as the original plan, or “none”.


## Results


### Data preparation

Data preparation following the analysis plan.
	
```{r include=F}
### Data Preparation

#### Load Relevant Libraries and Functions

#### Import data

#### Data exclusion / filtering

#### Prepare data for analysis - create columns etc.
```

### Confirmatory analysis

The analyses as specified in the analysis plan.  

*Side-by-side graph with original graph is ideal here*

### Exploratory analyses

Any follow-up analyses desired (not required).  

## Discussion

### Summary of Replication Attempt

Open the discussion section with a paragraph summarizing the primary result from the confirmatory analysis and the assessment of whether it replicated, partially replicated, or failed to replicate the original result.  

### Commentary

Add open-ended commentary (if any) reflecting (a) insights from follow-up exploratory analysis, (b) assessment of the meaning of the replication (or not) - e.g., for a failure to replicate, are the differences between original and present study ones that definitely, plausibly, or are unlikely to have been moderators of the result, and (c) discussion of any objections or challenges raised by the current and original authors about the replication attempt.  None of these need to be long.
