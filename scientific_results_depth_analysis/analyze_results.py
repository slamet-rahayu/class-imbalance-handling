"""Descriptive analysis of stored results only. No training or inferential tests."""
from pathlib import Path
import hashlib
import itertools
import json
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
METRICS=['brier_score','log_loss','ece']
STRATEGIES=['baseline','oversampling','class_weight']
NAMES={'baseline':'Baseline','oversampling':'ROS','class_weight':'CW'}
KEYS=['seed','imbalance_strategy','target_prevalence','calibration','prior_correction']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mdtable(frame):
    def fmt(x):
        if isinstance(x,(float,np.floating)): return f'{x:.6f}'
        return str(x)
    return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))

def main():
    source=ROOT/'outputs_confirmatory_30_seeds'
    inputs=[source/'all_repetitions.csv',source/'aggregate_summary.csv',source/'training_metadata.csv',source/'all_audits.csv',source/'execution_manifest.json',source/'output_hashes.json',ROOT/'confirmatory_protocol_v2.json',ROOT/'confirmatory_protocol_freeze_v2.json',ROOT/'scientific_validation_followup/METRIC_RECOMPUTATION.csv',ROOT/'scientific_validation_followup/predictions/MANIFEST.json',ROOT/'scientific_validation_followup/predictions/SCHEMA.json',ROOT/'scientific_validation_followup/FINAL_SCIENTIFIC_VALIDITY_DECISION.md',ROOT/'PREPROCESSING_AUDIT_REPORT.md',ROOT/'notebooks/results_and_discussion.ipynb']
    assert all(p.is_file() for p in inputs)
    before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    manifest=json.loads((source/'execution_manifest.json').read_text())
    assert manifest['protocol_version']=='confirmatory-30seed-v2'
    assert manifest['source_commit']=='2f448140cbdf5a593d1d182f26ef955d83cc717b'
    frozen=json.loads((source/'output_hashes.json').read_text())['files']
    assert all(sha(source/p)==h for p,h in frozen.items())
    df=pd.read_csv(inputs[0]); aggregate=pd.read_csv(inputs[1]); training=pd.read_csv(inputs[2]); audits=pd.read_csv(inputs[3])
    assert set(KEYS+METRICS+['sample_id_sha256','n_test'])<=set(df)
    assert df.prior_correction.dtype==bool
    assert not df[KEYS+METRICS+['sample_id_sha256']].isna().any().any()
    assert np.isfinite(df[METRICS]).all().all() and not df.duplicated(KEYS).any()
    expected=set(itertools.product(range(42,72),STRATEGIES,[.1,.155,.25],['raw','platt'],[False,True]))
    assert set(df[KEYS].itertuples(index=False,name=None))==expected and len(df)==1080
    v=pd.read_csv(ROOT/'scientific_validation_followup/METRIC_RECOMPUTATION.csv').rename(columns={'strategy':'imbalance_strategy'})
    long=df.melt(id_vars=KEYS,value_vars=METRICS,var_name='metric',value_name='original')
    verified=long.merge(v,on=KEYS+['metric'],validate='one_to_one')
    assert len(verified)==3240 and np.isclose(verified.original,verified.computed,atol=1e-12,rtol=1e-10).all()
    assert verified['match_atol_1e-12_rtol_1e-10'].eq(True).all()
    pred_manifest=json.loads((ROOT/'scientific_validation_followup/predictions/MANIFEST.json').read_text())
    for name,info in pred_manifest['files'].items(): assert sha(ROOT/'scientific_validation_followup/predictions'/name)==info['sha256']
    config_map={('raw',False):'Raw',('platt',False):'Platt',('raw',True):'Raw + Prior (exploratory)',('platt',True):'Platt + Prior'}
    df['configuration']=[config_map[x] for x in zip(df.calibration,df.prior_correction)]
    records=[]
    for (s,p,c),g in df.groupby(['imbalance_strategy','target_prevalence','configuration']):
        row={'strategy':s,'target_prevalence':p,'configuration':c,'analysis_scope':'exploratory' if c.startswith('Raw +') else 'main','n_splits':len(g)}
        for m in METRICS: row[m+'_mean']=g[m].mean();row[m+'_sd']=g[m].std(ddof=1)
        records.append(row)
    summary=pd.DataFrame(records)
    summary.to_csv(HERE/'SUPPORTING_METRICS_SUMMARY.csv',index=False,float_format='%.17g')
    paired_rows=[]; detail=[]
    def compare(label,a,b):
        keys=['seed','target_prevalence','sample_id_sha256']
        z=a.merge(b,on=keys,suffixes=('_a','_b'),validate='one_to_one')
        assert len(z)==len(a)==len(b)
        for c in ['n_test','n_positive','n_negative']: assert z[c+'_a'].equals(z[c+'_b'])
        for p,g in z.groupby('target_prevalence'):
            for m in METRICS:
                d=g[m+'_b']-g[m+'_a'];ma=g[m+'_a'].mean();mb=g[m+'_b'].mean()
                pattern='all improved' if (d<0).all() else 'all worsened' if (d>0).all() else 'all unchanged' if (d==0).all() else 'mixed'
                paired_rows.append({'comparison':label,'target_prevalence':p,'metric':m,'n_pairs':len(d),'mean_reference':ma,'mean_comparator':mb,'mean_paired_difference':d.mean(),'sd_paired_difference':d.std(ddof=1),'median_paired_difference':d.median(),'min_paired_difference':d.min(),'max_paired_difference':d.max(),'splits_improved':int((d<0).sum()),'splits_worsened':int((d>0).sum()),'splits_unchanged':int((d==0).sum()),'relative_change_percent':100*(mb-ma)/ma if ma!=0 else np.nan,'direction_pattern':pattern})
                for seed,h,delta in zip(g.seed,g.sample_id_sha256,d):detail.append({'comparison':label,'target_prevalence':p,'metric':m,'seed':seed,'sample_id_sha256':h,'delta':delta})
    for s in STRATEGIES:
        q=df[df.imbalance_strategy.eq(s)]
        qmain=q[q.target_prevalence.isin([.1,.25]) & q.calibration.eq('platt')]
        compare(NAMES[s]+' Platt + Prior vs Platt',qmain[~qmain.prior_correction],qmain[qmain.prior_correction])
        compare(NAMES[s]+' Platt vs Raw',q[q.calibration.eq('raw') & ~q.prior_correction],q[q.calibration.eq('platt') & ~q.prior_correction])
    base=df[df.imbalance_strategy.eq('baseline') & df.calibration.eq('raw') & ~df.prior_correction]
    for s in STRATEGIES[1:]:compare(NAMES[s]+' Raw vs Baseline Raw',base,df[df.imbalance_strategy.eq(s) & df.calibration.eq('raw') & ~df.prior_correction])
    pairs=pd.DataFrame(paired_rows); details=pd.DataFrame(detail)
    assert len(pairs)==63 and pairs.n_pairs.eq(30).all()
    assert (pairs.splits_improved+pairs.splits_worsened+pairs.splits_unchanged).eq(30).all()
    assert np.allclose(pairs.mean_paired_difference,pairs.mean_comparator-pairs.mean_reference,atol=1e-15)
    pairs.to_csv(HERE/'PAIRED_DESCRIPTIVE_VARIABILITY.csv',index=False,float_format='%.17g')
    details.to_csv(HERE/'PAIRED_SPLIT_DIFFERENCES.csv',index=False,float_format='%.17g')
    mainpairs=pairs[pairs.comparison.str.contains('Prior')]
    a=summary[summary.target_prevalence.eq(.155) & summary.configuration.isin(['Raw','Platt'])].drop(columns=['analysis_scope'])
    b=mainpairs[['comparison','target_prevalence','metric','mean_reference','mean_comparator','mean_paired_difference','sd_paired_difference','splits_improved','splits_worsened','splits_unchanged','relative_change_percent']]
    tables='# Manuscript Tables\n\n## Table A. Probability performance at nominal reference prevalence 0.155\n\n'+mdtable(a)+'\n\n## Table B. Effects of prior correction on probabilistic performance\n\n'+mdtable(b)
    tables+='\n\nBaseline: unweighted logistic regression; ROS: random oversampling; CW: class weighting; ECE: 10-bin equal-width expected calibration error; SD: sample standard deviation (ddof=1). Means and SDs describe 30 overlapping repetitions, not population inference. Delta = comparator minus reference; negative changes indicate improvement. Relative change = 100 × (mean comparator − mean reference) / mean reference. Use six decimal places for manuscript scores/SDs and two for percentage changes; retain full precision in CSV. Counts are exact integer counts, and unchanged means exact zero in stored values. Table A uses nominal 0.155, distinct from the source prevalence and realized scenario prevalence.\n\n## Supplementary Table C. Full main descriptive summaries\n\n'+mdtable(summary[summary.analysis_scope.eq('main')])
    tables+='\n\n## Supplementary Table D. Raw + Prior — exploratory only\n\n'+mdtable(summary[summary.analysis_scope.eq('exploratory')])
    (HERE/'MANUSCRIPT_TABLES.md').write_text(tables)
    literature=(HERE/'LITERATURE_EVIDENCE.md').read_text()
    raw_text=[];platt_text=[];prior_text=[]
    for name in ['ROS','CW']:
        g=pairs[(pairs.comparison.eq(name+' Raw vs Baseline Raw')) & pairs.target_prevalence.eq(.155)]
        raw_text.append(name+' versus Baseline at nominal 0.155: '+ '; '.join(f'{r.metric} {r.mean_reference:.6f} → {r.mean_comparator:.6f} (delta {r.mean_paired_difference:+.6f}; {r.splits_worsened}/30 worsened)' for r in g.itertuples())+'.')
    for name in ['Baseline','ROS','CW']:
        g=pairs[pairs.comparison.eq(name+' Platt vs Raw') & pairs.target_prevalence.eq(.155)]
        platt_text.append(name+' calibration at nominal 0.155: '+'; '.join(f'{r.metric} delta {r.mean_paired_difference:+.6f} ({r.relative_change_percent:+.2f}%; {r.splits_improved}/30 improved)' for r in g.itertuples())+'.')
    for r in mainpairs.itertuples():
        prior_text.append(f'{r.comparison}, target {r.target_prevalence:.2f}, {r.metric}: {r.mean_reference:.6f} → {r.mean_comparator:.6f}; delta {r.mean_paired_difference:+.6f}, SD {r.sd_paired_difference:.6f}, median {r.median_paired_difference:+.6f}, range [{r.min_paired_difference:+.6f}, {r.max_paired_difference:+.6f}], relative change {r.relative_change_percent:+.2f}%; improved/worsened/unchanged {r.splits_improved}/{r.splits_worsened}/{r.splits_unchanged} ({r.direction_pattern}).')
    agreement=[]
    for (comparison,p),g in mainpairs.groupby(['comparison','target_prevalence']):
        bs=g[g.metric.eq('brier_score')].iloc[0]
        for r in g[g.metric.ne('brier_score')].itertuples():
            agreement.append({'comparison':comparison,'target_prevalence':p,'supporting_metric':r.metric,'brier_mean_delta':bs.mean_paired_difference,'supporting_mean_delta':r.mean_paired_difference,'mean_direction_agrees':bool(np.sign(bs.mean_paired_difference)==np.sign(r.mean_paired_difference))})
    agreement=pd.DataFrame(agreement);agreement.to_csv(HERE/'METRIC_DIRECTION_AGREEMENT.csv',index=False,float_format='%.17g')
    limitations='Thirty overlapping splits describe a finite dataset and fixed pipeline. Improvement counts are not population success probabilities. Oracle correction used realized test-subset prevalence, so unknown-prior deployment effectiveness was not evaluated. ECE is a bin-based estimate affected by sample size, bin boundaries and probability distribution; it is not a Brier decomposition. No universal superiority or causal mechanism is established. Freeze chronology remains inconclusive. Duplicate-valued rows and feature-availability risks remain as documented in PREPROCESSING_AUDIT_REPORT.md. No new fitting, resampling, simulations, or inferential procedures were performed.'
    interpretation='ROS changes the class distribution seen during fitting and CW changes the weighted fitting objective. These mechanisms can change the probability scale relative to natural prevalence; the observed raw error increases are consistent with this explanation but do not isolate it causally. Platt calibration learns a new probability mapping on the natural calibration partition and can reduce these differences. Baseline already reflects natural training prevalence, and finite calibration data, model misspecification, and calibration regularization can plausibly limit or reverse its gain; none of these mechanisms was isolated here. Bayes correction is exact only under its source-probability and pure-label-shift assumptions. Imperfect source calibration and finite-sample variation can coexist with small worsening at low prevalence. Brier measures squared probability error, log loss penalizes confident errors strongly, and ECE averages bin discrepancies; disagreement does not identify a proven cause. For purchase prediction, validate probability quality and practical decision thresholds on appropriate target data rather than selecting a strategy from rebalancing or discrimination alone.'
    sources='Primary file: outputs_confirmatory_30_seeds/all_repetitions.csv. Keys: seed, imbalance_strategy, target_prevalence, calibration, prior_correction; pairing adds sample_id_sha256 and validates sample counts. Metrics: brier_score, log_loss, ece. Row project_version=stage1-remediation-v1 is a source-code label; v2 identity is established by execution_manifest.json, protocol and source commit, not that label alone. No historical 10-seed outputs were pooled. aggregate_summary.csv means were checked against recomputed means. training_metadata.csv and all_audits.csv provide training/scenario counts; prediction files are regenerated audit outputs, not original contemporaneous exports. The existing notebook is a reporting consumer and was inspected without execution. No reference PDF/bibliography for the named studies was found in repository searches; online sources are documented separately.'
    ag=df.groupby(['imbalance_strategy','calibration','target_prevalence','prior_correction'])[METRICS].mean().reset_index().merge(aggregate,on=['imbalance_strategy','calibration','target_prevalence','prior_correction'],validate='one_to_one')
    assert len(ag)==36
    for metric in METRICS: assert np.allclose(ag[metric],ag[metric+'_mean'],atol=1e-15)
    report='# Scientific Results Depth Analysis\n\n## 1. Executive Summary\n\nStored experiment data were complete and consistent: 30 seeds, 1,080 metric rows, 36 configurations and 3,240 verified metric comparisons. Main summaries contain 27 configurations; nine Raw + Prior configurations are exploratory. All additional comparisons are descriptive.\n\n## 2. Data Sources and Verification\n\n'+sources+'\n\nInput hashes and execution metadata are recorded in VALIDATION_MANIFEST.json. Prediction manifest: '+str(len(pred_manifest['files']))+' hashed files.\n\n## 3. Supporting Metrics Results\n\n'+'\n\n'.join(raw_text+platt_text)+'\n\nFull scenario results and mean/SD/n are in SUPPORTING_METRICS_SUMMARY.csv and MANUSCRIPT_TABLES.md.\n\n## 4. Paired Descriptive Variability\n\n'+'\n\n'.join(prior_text)+'\n\nAll additional comparisons span all three prevalences, yielding 63 comparison–scenario–metric rows and 1,890 recorded seed-level differences. The relative-change denominator is the mean reference metric, not the comparator or the mean of per-seed ratios.\n\n## 5. Consistency Across Repeated Splits\n\n'+mdtable(pairs[['comparison','target_prevalence','metric','splits_improved','splits_worsened','splits_unchanged','direction_pattern']])+'\n\n### Agreement with Brier direction\n\n'+mdtable(agreement)+'\n\n## 6. Comparison with Previous Studies\n\n'+literature+'\n\n## 7. Scientific Interpretation\n\n'+interpretation+'\n\n## 8. Limitations of the Analysis\n\n'+limitations+'\n\n## 9. Recommended Manuscript Revisions\n\nAdd Table A for reference calibration and Table B for paired correction effects. Report delta SD and full empirical range as split variability. Keep Raw + Prior in the exploratory supplement. Distinguish mean-direction agreement from all-split agreement. Use author–year citations only within the evidence scope stated in LITERATURE_EVIDENCE.md. Avoid equating low ECE with complete calibration or low Brier.\n\n## 10. Final Conclusions\n\nThe stored results support a prevalence-dependent descriptive account of probability quality. Supporting metrics can agree in direction with Brier in some conditions and disagree in others; the explicit counts and differences above preserve this distinction. The findings characterize this dataset and pipeline, without population inference.\n'
    (HERE/'RESULTS_DEPTH_ANALYSIS.md').write_text(report)
    draft='# Results and Discussion — Revision Draft\n\n## 3.2 Effects of Imbalance Handling and Calibration\n\n'+' '.join(raw_text)+'\n\n'+' '.join(platt_text)+'\n\nThese changes describe the thirty specified overlapping splits. Rebalancing altered raw probability performance, whereas fitting a separate probability mapping on the natural calibration sample reduced much of the observed error for ROS and CW. This pattern is compatible with, but does not demonstrate, a probability-scale explanation.\n\n## 3.3 Prior Probability Correction\n\n'+'\n\n'.join(prior_text)+'\n\nNegative paired differences denote improvement. The high- and low-prevalence scenarios should be interpreted separately rather than collapsed into an overall claim of benefit. Mean changes, variation, and directional counts are descriptive characteristics of this split schedule.\n\n## 3.4 Discussion\n\n'+interpretation+'\n\nThe reference-scenario pattern is qualitatively compatible with the calibration concerns reported by van den Goorbergh et al. (2022) and Piccininni et al. (2024). These studies evaluated clinical risk prediction and different correction designs; their findings do not directly validate the present purchase-prediction experiment. Ledwaba and Mokoena (2026), as reported in the publisher abstract, examined calibration and prior correction across multiple datasets and models. That broader setting offers context, not a replication of the present design. See LITERATURE_EVIDENCE.md for verified titles, authors, source sections, and scope limitations.\n\n'+limitations+'\n'
    (HERE/'RESULTS_DISCUSSION_DRAFT.md').write_text(draft)
    assert all(sha(ROOT/p)==h for p,h in before.items())
    assert all(sha(source/p)==h for p,h in frozen.items())
    out={'status':'PASS','input_sha256':before,'protocol_version':manifest['protocol_version'],'source_commit':manifest['source_commit'],'metric_records':len(df),'seeds':int(df.seed.nunique()),'configurations':len(summary),'paired_summary_rows':len(pairs),'paired_split_metric_differences':len(details),'metric_verification_rows':len(verified),'mismatches':0,'frozen_hashes_unchanged':len(frozen),'definitions':{'SD':'sample ddof=1','delta':'comparator minus reference','relative_change_percent':'100*(mean comparator-mean reference)/mean reference'},'output_files':sorted(p.name for p in HERE.iterdir() if p.is_file())}
    (HERE/'VALIDATION_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
    for name in ['SUPPORTING_METRICS_SUMMARY.csv','PAIRED_DESCRIPTIVE_VARIABILITY.csv']:
        loaded=pd.read_csv(HERE/name);assert not loaded.empty
    print(json.dumps({k:v for k,v in out.items() if k not in ['input_sha256','output_files']},indent=2))

if __name__=='__main__': main()
