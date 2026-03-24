import topomt as tmt
import molsysmt as msm

pdb_id = '1tcd'
methods = ['pocketeer', 'alphaspace2', 'fpocket', 'castp', 'pycasta']

print(f"Comparing pocket detection methods for {pdb_id}...")

topographies = {}

for method in methods:
    print(f"\n--- Running {method} ---")
    try:
        topo = tmt.get_topography(pdb_id, method=method)
        topographies[method] = topo
        pockets = topo.get_features(by='type', value='pocket')
        print(f"Method {method} found {len(pockets)} pockets.")
        
        if len(pockets) > 0:
            # Show first pocket info
            p0_id = list(topo.keys())[0]
            p0 = topo[p0_id]
            print(f"  First pocket ({p0_id}): center={p0.center}, volume={p0.volume:.2f}, atoms={len(p0.atom_indices)}")
            
    except Exception as e:
        print(f"  Error running {method}: {e}")
        import traceback
        traceback.print_exc()

print("\nSummary of results:")
for method in methods:
    topo = topographies.get(method)
    if topo:
        n_pockets = len(topo.get_features(by='type', value='pocket'))
        print(f"  - {method:12}: {n_pockets} pockets")
    else:
        print(f"  - {method:12}: FAILED")

print("\nTest finished!")
