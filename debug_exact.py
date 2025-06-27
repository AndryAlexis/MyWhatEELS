#!/usr/bin/env python3
"""Debug script to reproduce the Column replace error"""

import os
import sys
from whateels.helpers.file_reader.file_reader import DM_EELS_Reader
from whateels.helpers.visual_displays import Visual_loading
import xarray as xr
import numpy as np

def debug_column_error():
    """Debug the exact issue with Column replace error"""
    
    # Test with the BEF03_0009.dm4 file
    test_file = os.path.join(os.path.dirname(__file__), 'BEF03_0009.dm4')
    
    try:
        print("📖 Reading DM4 file...")
        reader = DM_EELS_Reader(test_file)
        si = reader.read_data()
        print('DATA LOADED', si.data.shape, si.data.dtype)
        
        # Get data and energy axis
        data = si.data
        E = si.energy_axis
        print('ENERGY AXIS', E.shape, E.dtype)
        
        # Reproduce the exact same logic as DMFileViewer
        if len(data.shape) == 3:
            # For spectrum images: (Eloss, Y, X) -> (Y, X, Eloss)
            data = data.transpose((1, 2, 0))
            type_dataset = 'SIm'
            ys = np.arange(0, data.shape[0])
            xs = np.arange(0, data.shape[1])
        elif len(data.shape) == 2:
            # For spectrum lines: (Eloss, X) -> (X, 1, Eloss)
            type_dataset = 'SLi'
            ys = np.arange(0, data.shape[1])
            xs = np.zeros((1), dtype=np.int32)
            shap = list(data.shape)
            shap.insert(1, 1)
            data = data.reshape(shap)
        elif len(data.shape) == 1:
            # For single spectra: (Eloss,) -> (1, 1, Eloss)
            type_dataset = 'SSp'
            xs = np.zeros((1), dtype=np.int32)
            ys = np.zeros((1), dtype=np.int32)
            shap = [1, 1]
            shap.extend(list(data.shape))
            data = data.reshape(shap)
        else:
            print(f"Unexpected data shape: {data.shape}")
            return None
        
        print(f"Dataset type: {type_dataset}")
        print(f"Final data shape: {data.shape}")
        
        # Validate coordinate types
        print('COORDINATES:', type(ys), type(xs), type(E))
        print('COORDINATE SHAPES:', ys.shape if hasattr(ys, 'shape') else len(ys), 
              xs.shape if hasattr(xs, 'shape') else len(xs), 
              E.shape if hasattr(E, 'shape') else len(E))
        
        # Create xarray dataset
        ds = xr.Dataset(
            {'ElectronCount': (['y', 'x', 'Eloss'], data)},
            coords={'y': ys, 'x': xs, 'Eloss': E}
        )
        
        # Add metadata
        ds.attrs['original_name'] = os.path.basename(test_file)
        
        print("📊 Dataset created successfully")
        print(f"Dataset coords: {list(ds.coords.keys())}")
        print(f"Dataset data_vars: {list(ds.data_vars.keys())}")
        
        print("🎨 Creating Visual_loading...")
        viz = Visual_loading(ds)
        print("✅ Visual_loading created successfully!")
        
        print("🏗️ Creating panels...")
        viz.create_panels()
        print("✅ Panels created successfully!")
        
        print("🔍 Testing struc attribute...")
        print(f"viz.struc type: {type(viz.struc)}")
        print("✅ All tests passed!")
        
        return viz
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print("📋 Full traceback:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_column_error()
