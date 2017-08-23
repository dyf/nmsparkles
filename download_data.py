from allensdk.core.brain_observatory_cache import BrainObservatoryCache
import pandas as pd
import time
import numpy as np
import allensdk.brain_observatory.stimulus_info as si
from sklearn import manifold

def compute_mean_response(boc, cell_id, stim, session):
    exp = boc.get_ophys_experiments(cell_specimen_ids=[cell_id], 
                                    stimuli=[stim], 
                                    session_types=[session])[0]
    ds = boc.get_ophys_experiment_data(exp['id'])

    _, dff = ds.get_dff_traces(cell_specimen_ids=[cell_id])
    dff = dff[0]
    
    stim_table = ds.get_stimulus_table(stim)
    repeat_dffs = []
    for i in range(stim_table.repeat.min(), stim_table.repeat.max()+1):
        repeat_table = stim_table[stim_table.repeat == i]
        fmin = repeat_table.start.min()
        fmax = repeat_table.end.max()
        repeat_dffs.append((fmin, fmax))

    minlen = min((fmax-fmin) for rdff in repeat_dffs)
    arr = np.zeros((len(repeat_dffs), minlen))    
    for r_i, (fmin, fmax) in enumerate(repeat_dffs):
        arr[r_i] = dff[fmin:fmin+minlen]    
    return arr.mean(axis=0)

def download_data(boc, stim, session, metric, threshold, out_file, template_file):
    exps = boc.get_ophys_experiments(stimuli=[stim])
    cells = pd.DataFrame.from_records(boc.get_cell_specimens())
    nm_cells = cells[cells[metric] > thresold]

    arrs = []
    for i,cell_id in enumerate(nm_cells.cell_specimen_id):
        tstart = time.time()
        mr = compute_mean_response(boc, cell_id, stim, session)
        print("computed %d/%d (%f)" % (i+1,len(nm_cells), time.time()-tstart))
        arrs.append(mr)

    minlen = min(arr.shape[0] for arr in arrs)
    big_arr = np.vstack([ arr[:minlen] for arr in arrs])

    mds = manifold.TSNE(n_components=2)
    pos = mds.fit_transform(big_arr)

    np.savez_compressed(out_file, pos=pos, arr=big_arr)

    nm_t = boc.get_ophys_experiment_data(exps[0]['id']).get_stimulus_template(stim)
    np.savez_compressed(template_file, template=nm1_t)


def main():
    manifest_file = '/data/dynamic-brain-workshop/brain_observatory_cache/brain_observatory_manifest.json'
    boc = BrainObservatoryCache(manifest_file=manifest_file)

    stim = si.NATURAL_MOVIE_THREE
    session = si.THREE_SESSION_A
    metric = 'reliability_nm3'
    threshold = .5
    out_file = 'sparkles_nm3_2d.npz'
    template_file  = 'nm3.npz'

    download_data(boc, stim, session, metric, threshold, out_file, template_file)

if __name__ == "__main__": main()