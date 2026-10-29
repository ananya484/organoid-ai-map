"""Figures for the systematic map (300 dpi, Okabe-Ito). Reads results/*.json only."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'results'); FIG = os.path.join(ROOT, 'figures'); os.makedirs(FIG, exist_ok=True)
S = json.load(open(os.path.join(RES, 'summary.json')))
F = json.load(open(os.path.join(RES, 'fulltext_summary.json')))
CT = json.load(open(os.path.join(RES, 'crosstab_application_validation.json')))
RV = json.load(open(os.path.join(RES, 'review_relevance.json')))
OI = ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
plt.rcParams.update({'font.size': 8, 'font.family': 'DejaVu Sans', 'axes.linewidth': 0.7, 'legend.frameon': False,
                     'savefig.dpi': 300, 'savefig.bbox': 'tight', 'axes.spines.top': False, 'axes.spines.right': False})
NICE = {'segmentation_detection': 'segmentation / detection', 'omics_analysis': 'omics analysis',
        'morphology_classification': 'morphology classification', 'drug_response_prediction': 'drug-response prediction',
        'signal_analysis': 'signal analysis', 'tracking_timelapse': 'tracking / time-lapse',
        'toxicity_prediction': 'toxicity prediction', 'system_design_optimisation': 'system design / optimisation',
        'generative_or_llm': 'generative / LLM', 'other': 'other', 'method_development': 'method development',
        'disease_modelling': 'disease modelling', 'drug_efficacy_screening': 'drug efficacy screening',
        'quality_control': 'quality control', 'personalised_medicine': 'personalised medicine',
        'toxicity_safety': 'toxicity / safety', 'device_or_protocol_design': 'device / protocol design',
        'intestine_colon': 'intestine / colon', 'tumour_other': 'tumour (other)', 'multi': 'multiple',
        'bone_cartilage': 'bone / cartilage', 'none_reported': 'none reported', 'internal_split_or_cv': 'internal split / CV',
        'external_dataset': 'external dataset', 'experimental_prospective': 'prospective experiment',
        'clinical_outcome': 'clinical outcome'}
nice = lambda k: NICE.get(k, k)


def box(ax, x, y, w, h, text, fc='white'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02', fc=fc, ec='k', lw=0.7))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=7)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', lw=0.7))


def fig1():
    fig, ax = plt.subplots(figsize=(6.2, 5.0)); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    box(ax, 0.5, 8.6, 4.6, 1.0, f"Records from Europe PMC\n(searched {S['search_date']})\nn = {S['search_hits']:,}")
    box(ax, 5.8, 8.35, 3.9, 1.5, f"Removed before screening\nreview publication type: {S['dedupe_excluded_review_pubtype']}\n"
                                f"preprint of published record: {S['dedupe_excluded_preprint_of_published']}\n"
                                f"no abstract: {S['dedupe_excluded_no_abstract']}; duplicate: {S['dedupe_excluded_duplicate']}")
    arrow(ax, 5.1, 9.1, 5.8, 9.1)
    box(ax, 0.5, 6.4, 4.6, 1.0, f"Titles and abstracts screened\nn = {S['screened']}")
    arrow(ax, 2.8, 8.6, 2.8, 7.4)
    er = S['exclude_reasons']
    box(ax, 5.8, 5.9, 3.9, 2.0, f"Excluded, n = {S['excluded']}\nAI on other data, organoid\nonly for validation / other: {er.get('other', 0)}\n"
                                f"not a primary study: {er.get('not_primary', 0)}\nno AI method: {er.get('no_ai', 0)}\n"
                                f"no organoid or chip: {er.get('no_organoid_or_chip', 0)}\norganoid biocomputing: {er.get('organoid_intelligence_computing', 0)}")
    arrow(ax, 5.1, 6.9, 5.8, 6.9)
    box(ax, 0.5, 4.2, 4.6, 1.0, f"Eligible records\nn = {S['included_before_dedupe']}")
    arrow(ax, 2.8, 6.4, 2.8, 5.2)
    box(ax, 5.8, 4.2, 3.9, 1.0, f"Preprint and journal version\nof the same study merged: {S['duplicates_removed']}")
    arrow(ax, 5.1, 4.7, 5.8, 4.7)
    box(ax, 0.5, 2.0, 4.6, 1.0, f"Studies in the map\nn = {S['included']}", fc='#e8f3fb')
    arrow(ax, 2.8, 4.2, 2.8, 3.0)
    box(ax, 5.8, 2.0, 3.9, 1.0, f"Open-access full text checked\nfor code/data links: n = {F['fulltext_n']}")
    arrow(ax, 5.1, 2.5, 5.8, 2.5)
    fig.savefig(os.path.join(FIG, 'Fig1.png')); plt.close(fig)


def fig2():
    yrs = list(range(2018, 2027))
    inc = [S['included_by_year'].get(str(y), 0) for y in yrs]
    rev = [S['reviews_by_year'].get(str(y), 0) for y in yrs]
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    x = np.arange(len(yrs))
    ax.bar(x - 0.2, inc, 0.4, color=OI[5], label='primary AI studies (this map)')
    lo, hi = RV['pct_ontopic_both'] / 100, RV['pct_ontopic_either'] / 100
    ax.bar(x + 0.2, rev, 0.4, fc='none', edgecolor=OI[1], hatch='///', lw=0.6, label='indexed as review (all topics)')
    est = np.array(rev) * lo
    ax.bar(x + 0.2, est, 0.4, color=OI[1], label='estimated relevant reviews')
    ax.errorbar(x + 0.2, est, yerr=[np.zeros(len(rev)), np.array(rev) * (hi - lo)], fmt='none', ecolor='k', lw=0.7, capsize=2)
    ax.set_xticks(x); ax.set_xticklabels([str(y) if y < 2026 else '2026*' for y in yrs])
    ax.set_ylabel('records'); ax.legend(loc='upper left')
    ax.text(0.99, -0.22, '*to ' + S['search_date'], transform=ax.transAxes, ha='right', fontsize=6)
    fig.savefig(os.path.join(FIG, 'Fig2.png')); plt.close(fig)


def hbar(ax, d, title, color, top=10):
    items = list(d.items())[:top][::-1]
    ax.barh([nice(k) for k, _ in items], [v for _, v in items], color=color)
    for i, (_, v) in enumerate(items):
        ax.text(v + 0.5, i, str(v), va='center', fontsize=6.5)
    ax.set_title(title, fontsize=8, loc='left')


def fig3():
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.0))
    hbar(axs[0], S['n_tissue'], 'a  tissue', OI[2])
    hbar(axs[1], S['n_ai_task'], 'b  AI task', OI[3])
    hbar(axs[2], S['n_application'], 'c  application', OI[6])
    for a in axs:
        a.set_xlabel('studies')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'Fig3.png')); plt.close(fig)


def fig4():
    n = S['included']
    steps = [('in the map', n),
             ('any validation reported', n - S['validation_highest']['none_reported']),
             ('beyond internal split / CV', S['n_beyond_internal']),
             ('compared with in vivo outcome', S['n_any_in_vivo_benchmark']),
             ('clinical outcome as reference', S['n_clinical_outcome']),
             ('compared with animal data', S['n_animal_benchmark']),
             ('regulatory / NAM context stated', S['n_regulatory'])]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axs[0]
    for i, (lab, v) in enumerate(steps):
        ax.barh(len(steps) - 1 - i, v, color=OI[5] if i == 0 else OI[6], alpha=1 if i == 0 else 0.85)
        ax.text(v + 3, len(steps) - 1 - i, f'{v} ({100 * v / n:.1f}%)', va='center', fontsize=6.5)
    ax.set_yticks(range(len(steps))); ax.set_yticklabels([s[0] for s in steps][::-1])
    ax.set_xlim(0, n * 1.25); ax.set_xlabel('studies (from abstracts)'); ax.set_title('a  evidence that would matter to a regulator', fontsize=8, loc='left')
    ax = axs[1]
    labs = ['abstract:\nopen', 'full text:\ncode or data', 'full text:\ncode']
    vals = [S['pct_open'], F['fulltext_pct_any_link'], F['fulltext_pct_code_link']]
    ax.bar(range(3), vals, color=[OI[7], OI[3], OI[3]], edgecolor='k', lw=0.4, hatch=['', '', '..'])
    for i, v in enumerate(vals):
        ax.text(i, v + 1.5, f'{v:.1f}%', ha='center', fontsize=6.5)
    ax.set_xticks(range(3)); ax.set_xticklabels(labs, fontsize=6.5); ax.set_ylim(0, 80); ax.set_ylabel('% of studies')
    ax.set_title(f"b  openness (full text: n = {F['fulltext_n']})", fontsize=8, loc='left')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'Fig4.png')); plt.close(fig)


def fig5():
    apps = sorted(CT, key=lambda a: -sum(CT[a].values()))
    vals = ['none_reported', 'internal_split_or_cv', 'external_dataset', 'experimental_prospective', 'clinical_outcome']
    M = np.array([[CT[a][v] for v in vals] for a in apps], float)
    P = M / M.sum(1, keepdims=True) * 100
    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    im = ax.imshow(P, cmap='cividis', vmin=0, vmax=100, aspect='auto')
    for i in range(len(apps)):
        for j in range(len(vals)):
            ax.text(j, i, f'{int(M[i, j])}', ha='center', va='center', fontsize=6.5, color='white' if P[i, j] < 55 else 'black')
    ax.set_xticks(range(len(vals))); ax.set_xticklabels([nice(v) for v in vals], rotation=30, ha='right')
    ax.set_yticks(range(len(apps))); ax.set_yticklabels([f'{nice(a)} (n={int(M[i].sum())})' for i, a in enumerate(apps)])
    cb = fig.colorbar(im, ax=ax); cb.set_label('% of row', fontsize=7)
    ax.set_xlabel('highest validation reported in the abstract')
    fig.savefig(os.path.join(FIG, 'Fig5.png')); plt.close(fig)


def graphical_abstract():
    fig = plt.figure(figsize=(11 / 1.5, 6 / 1.5))
    fig.text(0.5, 0.91, 'AI on organoids and organs-on-chips: ready to replace animal tests?', ha='center', fontsize=11.5, fontweight='bold')
    stats = [(f"{S['included']}", 'primary AI studies\nmapped (2018–2026)'),
             (f"~{RV['ratio_ontopic_reviews_per_study_high']:.0f}:1", 'relevant reviews\nper study'),
             (f"{S['pct_beyond_internal']:.0f}%", 'validated beyond\nan internal split'),
             (f"{S['n_animal_benchmark']}", 'compared with\nanimal data')]
    for i, (big, small) in enumerate(stats):
        x = 0.13 + i * 0.245
        fig.text(x, 0.6, big, ha='center', fontsize=24, fontweight='bold', color=[OI[5], OI[1], OI[6], OI[6]][i])
        fig.text(x, 0.44, small, ha='center', fontsize=8.5)
    fig.text(0.5, 0.2, 'Open, searchable database of every study + a minimum reporting checklist', ha='center', fontsize=9.5)
    fig.text(0.5, 0.09, 'Systematic map of Europe PMC; 3 independent coders, Fleiss κ = 0.95', ha='center', fontsize=8, style='italic')
    with plt.rc_context({'savefig.bbox': 'standard'}):
        fig.savefig(os.path.join(FIG, 'graphical_abstract.png'), dpi=300)
    plt.close(fig)


if __name__ == '__main__':
    fig1(); fig2(); fig3(); fig4(); fig5(); graphical_abstract(); print('ok')
