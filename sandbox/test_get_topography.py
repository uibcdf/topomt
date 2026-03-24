import topomt as tmt

try:
    # Use a small PDB for testing, e.g., 1TCD (Triosephosphate isomerase)
    pdb_id = '1tcd'
    print(f"Running get_topography for {pdb_id} using pocketeer...")
    topo = tmt.get_topography(pdb_id, method='pocketeer')
    
    print(f"Topography generated: {topo}")
    print(f"Number of pockets: {len(topo.get_features(by='type', value='pocket'))}")
    
    if len(topo) > 0:
        first_feature_id = list(topo.keys())[0]
        print(f"Details of first feature ({first_feature_id}):")
        print(topo[first_feature_id])
        
    print("Success!")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
