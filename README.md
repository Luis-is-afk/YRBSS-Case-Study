# CDC YRBSS Case Study: Academic Performance and Youth Mental Health

## Tools Used

Python (`pandas`, `statsmodels`, `numpy`, `tabulate`), Markdown, Git, and GitHub.

**Dataset:** 2023 CDC Youth Risk Behavior Surveillance System (YRBSS) National Microdata (`n ≈ 13,000`)

**Source:** [CDC Youth Risk Behavior Surveillance System](https://www.cdc.gov/healthy-youth/yrbs/index.htm)

> The raw microdata used in this repository was retrieved directly from the CDC before recent federal website updates and URL restructuring. To support reproducibility and reduce reliance on external links, the dataset structure used for this analysis is preserved locally in `/data`.

## Summary

This case study examines whether a teenager's self reported grades are related to three serious mental health concerns: persistent sadness or hopelessness, seriously considering suicide, and making a suicide plan.

Using 2023 CDC YRBSS data, the analysis found a strong relationship between academic performance and reported mental health concerns. In general, students with lower grades reported these concerns more often than students with higher grades.

Among students reporting mostly A's, 20.0% reported persistent sadness or hopelessness. This increased to 80.1% among students reporting mostly D's. Serious suicidal thoughts increased from 6.9% among A students to 52.4% among D students, while reported suicide planning increased from 5.7% to 44.6%.

After adjusting for sex, age, race or ethnicity, sleep, school bullying, and cyberbullying, students with mostly D's had about 10 times the odds of reporting persistent sadness and about 9 times the odds of reporting a suicide plan compared with students reporting mostly A's.

These results do not prove that lower grades cause mental health problems. They do suggest that a major academic decline may be a useful reason for schools to offer a supportive check in. Grades should not be treated as a diagnosis or used as the only reason to intervene. They may instead serve as one early warning signal alongside other information about a student's well being.

## 1. Ask: Research Question and Stakeholders

### Research Question
To what extent are lower self reported high school grades associated with adolescent mental health concerns, including persistent sadness, serious suicidal thoughts, and suicide planning? Does this relationship remain after accounting for sleep, school bullying, cyberbullying, and demographic factors?
> Key metrics: The analysis uses weighted prevalence percentages and adjusted odds ratios to compare reported mental health outcomes across grade categories. The three outcomes are persistent sadness or hopelessness, seriously considering suicide, and making a suicide plan.
### Stakeholders

The intended audience includes school district leaders, state education departments, school counselors, student support teams, social workers, and education policy advisers.

The practical question is whether academic performance data could help schools identify students who may benefit from additional academic or personal support.
> **Client context:** This analysis is to be used by school mental health professionals or the state education department that wants to identify practical signals that may help schools offer support to students earlier.

## 2. Prepare: About the Data

This analysis uses data from the **2023 CDC Youth Risk Behavior Surveillance System (YRBSS)**. The YRBSS is a nationwide survey that collects information about health behaviors, school experiences, and mental health among U.S. high school students. The dataset contains roughly 13,000 respondents.

The survey uses a structured, multistage sampling process rather than selecting students completely at random. Schools and students are selected in groups and stages so that the results better represent high school students across the United States. The dataset includes a student weight for each respondent. These weights account for differences in how likely students were to be selected and help the estimates reflect the broader U.S. high school population.

- **File analyzed:** `yrbs2023.csv`
- **Approximate records:** 13,000 respondents
- **Student weight:** `weight`
- **Primary sampling unit:** `psu`
- **Sampling stratum:** `stratum`
- **Grade variable:** `q89` asks students, “During the past 12 months, how would you describe your grades in school?” Responses were grouped into five categories: Mostly A’s, Mostly B’s, Mostly C’s, Mostly D’s, and Mostly F’s. Responses such as “None of these” and “Not sure” were treated as missing. Mostly A’s were used as the comparison group in the regression models.
- **Mental health outcomes:** `qn26`, `qn27`, and `qn28`. These variables measure mental health challenges reported during the past 12 months: persistent feelings of sadness or hopelessness (`qn26`), seriously considering suicide (`qn27`), and making a suicide plan (`qn28`). Responses were recoded from the CDC format of 1 = Yes and 2 = No into binary values for analysis.

### Data Credibility

- **Reliable:** The data come from a large CDC survey conducted using standardized procedures.
- **Original:** The dataset is primary survey microdata released by the CDC.
- **Relevant:** It includes academic, demographic, behavioral, and mental health measures needed for this analysis.
- **Accessible:** The dataset is publicly available for research and analysis.

## 3. Process: Cleaning and Analysis

The analysis was run using Python stored in `analysis.py`.

### Data Cleaning and Variable Preparation

1. The mental health, school bullying, and cyberbullying variables were converted from the CDC's `1 = Yes` and `2 = No` format into binary values of `1` and `0`.
2. Self reported grades were grouped into five categories: Mostly A's, Mostly B's, Mostly C's, Mostly D's, and Mostly F's.
3. Responses such as “None of these” and “Not sure” were treated as missing for the grade analysis.
4. Sex, age, race or ethnicity, sleep, student weight, and sampling variables were cleaned for use in the analysis.
5. Mostly A's were used as the comparison group in the regression models.

### Statistical Methods

The analysis used two main approaches:

- **Weighted prevalence:** Student weights were used to estimate the percentage of students in each grade category reporting each mental health outcome.
- **Logistic regression:** Regression models estimated the odds of each outcome for students in each grade category compared with students reporting mostly A's.

The adjusted models included sex, age, race or ethnicity, sleep, school bullying, and cyberbullying. Student weights were used in the models, and standard errors were clustered by `psu`. Because each model drops rows missing any variable needed for that outcome, the regression sample sizes were 13,005 for persistent sadness, 12,969 for serious suicidal thoughts, and 12,979 for suicide planning.

An odds ratio describes how the odds of an outcome compare between two groups. For example, an adjusted odds ratio of 10 means that one group had about 10 times the odds of reporting the outcome as the comparison group after accounting for the other variables in the model. Odds ratios should not be interpreted as an exact percentage or as proof of cause and effect.

## 4. Analyze: Results

### Weighted Prevalence by Grade

| Academic grades | Persistent sadness or hopelessness | Seriously considered suicide | Made a suicide plan |
|:--|--:|--:|--:|
| Mostly A's | 20.0% | 6.9% | 5.7% |
| Mostly B's | 38.6% | 17.3% | 14.7% |
| Mostly C's | 58.6% | 31.9% | 23.3% |
| Mostly D's | 80.1% | 52.4% | 44.6% |
| Mostly F's | 74.4% | 52.0% | 43.7% |

The results show a clear pattern across the grade categories. Reported mental health concerns were more common among students with lower grades. The D category had the highest prevalence for all three outcomes, although the F category was slightly lower than the D category in each case.

### Adjusted Odds Ratios Compared with Mostly A's

| Outcome | Mostly B's | Mostly C's | Mostly D's | Mostly F's |
|:--|--:|--:|--:|--:|
| Persistent sadness or hopelessness | 2.10 (1.72–2.57) | 4.17 (3.52–4.95) | 10.33 (8.16–13.07) | 5.71 (4.12–7.92) |
| Seriously considered suicide | 2.02 (1.58–2.58) | 4.59 (3.75–5.62) | 9.15 (6.88–12.16) | 7.73 (5.65–10.57) |
| Made a suicide plan | 2.15 (1.77–2.61) | 4.06 (3.40–4.85) | 9.30 (7.07–12.24) | 7.72 (5.72–10.43) |

*Values are adjusted odds ratios with 95% confidence intervals. Mostly A's are the reference group. All reported p-values were below 0.001; the software displayed them as 0 because they were smaller than its reporting precision.*

### Main Findings in Plain Language

1. Students with lower grades reported mental health concerns more often than students with higher grades.
2. The relationship remained strong after accounting for sleep, bullying, cyberbullying, sex, age, and race or ethnicity.
3. Students reporting mostly D's had the highest reported prevalence and adjusted odds across the three outcomes.
4. Students reporting mostly F's also had substantially higher odds than A students, but their results were lower than the D group.
5. Academic success did not eliminate mental health concerns: one in five students reporting mostly A's still reported persistent sadness or hopelessness.

## 5. Share: Interpretation and Limitations

The results show an association between self reported grades and self reported mental health concerns. They do not show that lower grades directly cause sadness or suicidal thoughts. Mental health challenges may affect academic performance, academic pressure may affect mental health, or both may be influenced by factors not included in this analysis.

The D vs F pattern is also an observation, not a confirmed explanation. Students reporting mostly D's had higher values than students reporting mostly F's across all three outcomes, but this analysis cannot determine why. Possible explanations would need to be tested with additional research.

Other limitations include the following:

- The data are self reported and may include recall or reporting errors.
- The analysis is based on a survey collected at one point in time, so it cannot establish which factor came first.
- The models adjust for selected variables, but unmeasured factors may still influence the results.
- The analysis is intended to describe population level patterns, not diagnose individual students.
- The code uses student weights and clusters standard errors by `psu`, but it does not use the `stratum` variable directly in the reported models.

## 6. Act: Practical Recommendations

1. **Use academic decline as a prompt for support.** A substantial drop in grades could trigger a private, supportive checkin rather than an automatic disciplinary response.
2. **Pair academic and wellness support.** Tutoring, learning assistance, counseling referrals, and student support services should be considered together when a student is struggling.
3. **Avoid using grades as a diagnosis.** Academic performance should be one signal among several, not a stand alone measure of mental health risk.
4. **Protect privacy and use human review.** Any early warning system should limit access to sensitive information and require trained staff to review alerts before taking action.
5. **Offer immediate help when needed.** If a student reports suicidal thoughts or appears to be in immediate danger, staff should follow the school's established crisis-response procedures and connect the student with qualified mental health professionals.

**Final conclusion:** Lower self reported grades were strongly associated with higher reported levels of persistent sadness, serious suicidal thoughts, and suicide planning in this 2023 YRBSS sample. The association stil remains after adjusting for demographic factors, sleep, bullying, and cyberbullying. Academic decline should not be treated as a diagnosis, but it may be a useful signal for schools to offer timely academic and mental health support.

## Crisis and Mental Health Resources

This repository discusses adolescent mental health, depression, and suicidal behavior. If you or someone you know is struggling or in crisis, support is available.

- **988 Suicide & Crisis Lifeline:** Call or text **988** in the United States or Canada.
- **Crisis Text Line:** Text **HOME** to **741741** where available.
- **The Trevor Project:** Call **1-866-488-7386** or text **START** to **678-678**.
- **International support:** Find a local service through [Find A Helpline](https://findahelpline.com/).

If someone is in immediate danger, contact local emergency services or go to the nearest emergency department.
