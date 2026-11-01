# A Good Measurement Can Be a Bad Test

A measuring device can give the right answer while hiding the mistake in the model used to build it. This can happen without fraud, careless work, or an unusually unlucky sample. The same calculation that makes the answer useful can remove the evidence that something is wrong.

This matters when scientists use measurements to test a model that also helped produce those measurements. One response is to demand independent evidence. But independent in what sense? A different laboratory may use the same calculation. A different instrument may discard the same feature of its readings. Conversely, a calculation borrowed from the model under examination may leave its errors plainly visible.

I will defend a narrower requirement. Before agreement between a model and a reported measurement counts against a particular possible error, the reporting procedure must preserve some ability to reveal that error. This requirement concerns the path from observations to the claim made from them. It does not demand observations free of theory. More surprisingly, it does not require us to reject a measurement simply because it cannot test its own supporting model. A result may deserve trust for one purpose and deserve no weight for another.

## What the device reports

Consider an imagined instrument with two sensors. Each returns a number. The instrument is used to estimate a quantity, q, that both sensors respond to. Its working model says that each reading equals q plus a small random error. The errors have mean zero, are independent, and have the same known spread. For this example, assume their distributions are normal. Nothing depends on a claim that real instruments always behave this way.

The instrument reports the average of the two readings. This is a sensible way to estimate q under the working model. A positive random error in one reading can partly cancel a negative error in the other. Averaging many such pairs makes the estimate more precise.

Now suppose the working model misses a directional effect. The first sensor reads q plus d, while the second reads q minus d, with the same random errors as before. The quantity d is a stable effect of the arrangement. Perhaps the sensors face in opposite directions and the environment affects their responses differently. This is a proposed physical explanation, not a redefinition of q as whatever average happens to be recorded. Assume q has the same meaning in both models and that a separate reference method can estimate it.

The average is still centered on q. The positive and negative shifts cancel exactly. Its random spread is also unchanged. The working model and the alternative therefore predict exactly the same distribution of reported averages, for every fixed value of q. They differ in the individual readings: their difference is centered on zero under the working model and on 2d under the alternative.

Suppose a laboratory measures a reference object a thousand times. The reported averages fall close to the reference value. Their spread agrees with the advertised uncertainty. Another laboratory repeats the procedure with a separate device and gets the same result. This supports the claim that these devices estimate q well in these conditions. It provides no evidence that d is zero rather than nonzero, given the two models just described. All those results would look the same if the directional effect existed.

This is not merely a weak test that could be repaired by taking more observations. If the laboratory keeps only averages, no number of additional pairs will distinguish these alternatives under the stated assumptions. More observations make the answer to one question increasingly precise while leaving the other question untouched.

The example separates three claims. The reported average is a good estimate of q. The two sensors respond in the same way. The whole working model describes the instrument adequately. The first can be true while the second and third are false. Evidence for the first cannot be transferred to the others merely because all three claims appear in the same account of the instrument.

## The role of models

Measurement is often described as if the world supplies numbers which theory subsequently explains. Yet an instrument supplies a reading, and a model helps determine what that reading tells us about the object. Eran Tal develops this point by explaining how models guide the identification of a measured quantity, the treatment of error, and calibration. He also argues that objectivity does not require freedom from all models: agreement across suitable procedures and assumptions can justify attributing a result to the object. This provides the right starting point. The question is which claim a particular agreement supports. [Tal, 2024, §§3.2–4](https://doi.org/10.4324/9781003205647-23).

In the two-sensor example, the average can remain stable across genuine changes of procedure. One laboratory may use different materials, take more readings, or work with more accurate components. The common value need not be an illusion. The value q survives the proposed error in the model. What does not survive is an unrestricted inference from that stability to the correctness of the model's account of both sensors.

There are therefore two ways a result may be robust, meaning that it remains stable across changes. It can be stable because the changes give an error opportunities to show itself and no such error appears. It can also be stable because the reported result cancels that error. The second kind of stability can be excellent for measuring q. It cannot, by itself, tell us that the cancelled effect is absent.

This distinction does not challenge the value of agreement across instruments. It limits what follows from agreement. A measurement may be insensitive to a nuisance precisely because its designers succeeded. But an effect that is a nuisance for estimating one quantity can be the subject of the next scientific question. The success of the first project does not answer the second.

The problem is also not that averaging is inherently suspicious. If the rival model said that both readings shift upward by d, the average would retain the shift. Comparison with the reference method could then detect it. Whether the same reporting procedure is informative depends on the error at issue. The relevant unit of assessment is a procedure used to support a specified claim, not a procedure considered alone.

## Why some agreement says nothing

The general argument is simple. Start with possible full records: here, pairs of readings. A fixed reporting rule turns each record into a report. Different records can produce the same report. The pair 9 and 11 produces the same average as the pair 10 and 10.

Now consider two accounts of how the full records arise. If those accounts produce the same probabilities for every possible report, someone who receives only reports encounters the same evidence under either account. Any decision rule based only on those reports must behave in the same way under both. It cannot tend to detect one account while accepting the other. A change in prior confidence might still be reasonable for other reasons, but the reports themselves supply no distinction.

This conclusion requires equality of distributions over reports, not just two models happening to fit the average in one sample. Models may fit a current result equally well while making different predictions for future results. The example is stronger: the entire sequence of averages has the same distribution under the two accounts, assuming independent repetitions with the same q. The limitation belongs to what is reported.

These statistical ideas are established. Blocker and Meng explicitly warn that retaining enough information to estimate a parameter need not retain enough to check the assumptions used in preprocessing. Their work studies the consequences of passing processed data between stages of analysis. The present argument takes that warning into the philosophy of measurement; it does not offer a new theorem about statistical information. [Blocker and Meng, 2013, §3.1](https://arxiv.org/html/1309.6790v1).

The philosophical consequence is that we should distinguish a reason to trust a value from a reason to trust the wider account that produced it. The first reason can remain intact even when the second fails. To say that a measurement is dependent on a model does not tell us whether either reason is good. We have to inspect the particular dependence.

This also explains how a model can help test itself without a vicious circle. Under the working model, compute the average and then compare each reading with it. A directional effect appears as opposite departures from the average. The calculation uses the model's proposal that there is a common quantity to estimate. It nevertheless exposes a possible failure of the proposal that both sensors respond without a directional shift. The assumption guides a test with an outcome that could disagree with it.

Theory enters this test at several points. The readings must be recorded correctly. The two accounts share assumptions about random error. Interpreting a persistent difference as a directional effect may require further experiments. None of this removes the contrast between a test that retains the difference and one that erases it. Dependence on background assumptions is compatible with learning that a particular part of the working model needs repair.

## What passing a test can establish

Preserving a difference is necessary for detecting it, but it is not sufficient for a good test. The effect might be too small relative to noise. The sample might be too small. The instrument might be unstable. An apparent difference could be caused by a faulty connection instead of the proposed physical effect. A responsible test must address these possibilities.

Gelman and Shalizi emphasize that model checks should target particular errors that would matter for the inferences being made. A model can fit selected features and still fail elsewhere. Their approach already supports asking what a test could reveal, rather than treating agreement as a general stamp of approval. [Gelman and Shalizi, 2013, §§4.1–4.2](https://arxiv.org/html/1006.3868v4).

My requirement is an earlier question in that assessment. Before asking whether the available evidence is strong enough, ask whether the report retains the feature on which the proposed check depends. If it does not, better thresholds and larger samples of the same reports will not repair the problem. We need a different report or a different experiment.

This requirement has a limited scope. It does not say that an observation can confirm a model only if every conceivable rival has been ruled out. It applies when agreement is offered as a reason to dismiss a specified possible error. In the example, the claim that a directional response has been tested is false if only cancelling averages were examined. The average may still count against alternatives that predict a different average. A single result can be evidence in one comparison and silent in another.

Nor must scientists possess a complete rival theory. A persistent difference between the sensors can contradict an implication of the working model before anyone knows what causes it. The relevant possible error may initially be described only as a stable difference larger than the noise allows. Retaining the difference permits discovery. Explaining it comes later.

## What should be kept

The obvious practical advice is to keep the original readings. But that advice is too broad to be the conclusion. Some instruments generate more data than anyone can feasibly preserve. Records can also contain information whose storage carries real costs. Moreover, earlier readings are not automatically free of processing or assumptions. There is no guarantee that moving backward will eventually uncover a perfectly neutral foundation.

A better rule begins with the claims scientists intend to make. If the instrument is used only to estimate q, the average and a justified account of its uncertainty may be enough for that restricted task. If the same study claims to test whether the sensors respond equally, it must also retain evidence about their difference. In our simple example, keeping the average and the signed difference preserves both original numbers: add half the difference to the average to recover the first reading, and subtract it to recover the second.

Real cases will rarely be so convenient. Still, the reason for retaining additional material is precise. It keeps open the checks needed to support the study's own claims. An analyst should not advertise a report as evidence against an error when the report's construction removes every trace by which that error could appear.

There is a further choice when future questions are unknown. One cannot promise that a small summary will preserve all future uses. But neither must one save everything regardless of cost. Scientists can preserve selected earlier records, diagnostic differences, and information about how reports were computed. Such choices should be justified by the plausible future errors and questions they keep open. The value of a retained record includes the opportunity to discover that the current measurement model was wrong.

This is not merely a demand for reproducibility. Suppose a later researcher can reproduce every average exactly from a documented algorithm, but the separate sensor readings no longer exist. Reproducing the report does not restore the lost contrast. Conversely, retaining the readings without preserving how sensors were arranged may leave the difference impossible to interpret. What needs preservation is enough information to carry out and understand the relevant challenge, not merely enough to rerun a calculation.

## Can the average still be called a measurement?

A critic might insist that if the model of the instrument is wrong, its output cannot be a justified measurement of q. Perhaps all we possess is a coincidentally useful number.

Sometimes that is right. If we know nothing about why errors cancel, or whether they will keep cancelling, confidence in the output should fall. But the example allows a stronger situation. After finding a directional difference, investigators can develop and test a revised model under which the shifts are equal and opposite. They can also compare averages with the reference method across the conditions in which the device will be used. Those findings may justify the same estimate of q that the old model produced.

The model has changed while the measured value remains. This is neither proof that models are dispensable nor proof that the first model was secretly correct. It shows that the justification of a value can depend on less than the truth of every assumption previously used to obtain it. We may revise an explanation without withdrawing all the knowledge it helped us acquire.

There is a corresponding reason for caution. Cancellation established in one arrangement may fail when the instrument is moved or one sensor is replaced. The trustworthy claim should name its conditions. Retaining the separate readings makes it possible to investigate whether the mechanism that protects the average still holds. A good measurement today can become a bad measurement tomorrow if we mistake a local cancellation for a universal truth.

The central lesson concerns what agreement licenses us to say. In the example, exact agreement can support the usefulness of a measured value while giving no support at all to a claim about the absence of a directional effect. Model dependence is therefore not the decisive dividing line between good and bad evidence. The decisive question for a particular test is whether the route to the report leaves the tested error somewhere to appear. A procedure can deserve trust as a way of getting an answer even when that answer cannot vouch for the procedure's whole account of the world.

## References

Blocker, Alexander W., and Xiao-Li Meng. 2013. “The Potential and Perils of Preprocessing: Building New Foundations.” *Bernoulli* 19(4): 1176–1211. https://doi.org/10.3150/13-BEJSP16. Author text: https://arxiv.org/html/1309.6790v1.

Gelman, Andrew, and Cosma Rohilla Shalizi. 2013. “Philosophy and the Practice of Bayesian Statistics.” *British Journal of Mathematical and Statistical Psychology* 66: 8–38. https://doi.org/10.1111/j.2044-8317.2011.02037.x. Author text, version 4: https://arxiv.org/html/1006.3868v4.

Tal, Eran. 2024. “Models and Measurement.” In *The Routledge Handbook of Philosophy of Scientific Modeling*, 256–269. https://doi.org/10.4324/9781003205647-23.
