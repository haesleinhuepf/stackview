# Implementation Roadmap: Next Generation Stackview

## Overview

This document provides technical implementation details for the proposed features in NEXT_GENERATION_PROPOSALS.md. It focuses on architectural considerations, dependencies, and concrete implementation steps.

---

## Quick Wins: Features with High Impact, Low Effort

### 1. Enhanced Scale Bars (Issue #167)
**Effort**: Low | **Impact**: High | **Timeline**: 1-2 weeks

**Current Issue**: Users cannot easily add scale bars to exports
**Solution**: Integrate scale bar functionality into `imshow()`

**Implementation Steps**:
```python
# Add to _imshow.py
def imshow(image, 
           ...,
           scalebar=False,
           scalebar_length=None,  # in physical units
           scalebar_unit='µm',
           scalebar_location='bottom_right',
           scalebar_color='white',
           scalebar_thickness=3,
           scalebar_font_size=12,
           scale=1.0):  # units per pixel
    
    if scalebar:
        from matplotlib_scalebar.scalebar import ScaleBar
        # Add scale bar to matplotlib plot
        scalebar_obj = ScaleBar(
            scale, 
            scalebar_unit,
            location=scalebar_location,
            color=scalebar_color,
            box_alpha=0,
            scale_loc='none' if scalebar_length else 'bottom'
        )
        ax.add_artist(scalebar_obj)
```

**Dependencies**: 
- Add `matplotlib-scalebar` to setup.py
- Consider optional dependency to keep core lightweight

**Tests**:
- Test scale bar rendering at different locations
- Test with various image sizes
- Test export with scale bar

---

### 2. Keyboard Shortcuts
**Effort**: Medium | **Impact**: High | **Timeline**: 2-3 weeks

**Current Issue**: All interactions require mouse/touch
**Solution**: Add keyboard event handling to widgets

**Implementation Steps**:

```python
# Add to _slice_viewer.py or create _keyboard_handler.py
class KeyboardHandler:
    def __init__(self, viewer):
        self.viewer = viewer
        self.shortcuts = {
            'ArrowUp': lambda: self._change_slice(-1),
            'ArrowDown': lambda: self._change_slice(1),
            '+': lambda: self._zoom(1.2),
            '-': lambda: self._zoom(0.8),
            'r': lambda: self._reset_view(),
            'h': lambda: self._toggle_controls(),
        }
    
    def handle_keypress(self, event):
        key = event['key']
        if key in self.shortcuts:
            self.shortcuts[key]()
    
    def _change_slice(self, delta):
        current = self.viewer.sliders[0].value
        new_value = max(0, min(self.viewer.sliders[0].max, current + delta))
        self.viewer.sliders[0].value = new_value

# Integrate with ipyevents
from ipyevents import Event
keyboard_event = Event(source=widget, watched_events=['keydown'])
keyboard_event.on_dom_event(keyboard_handler.handle_keypress)
```

**Considerations**:
- Need to handle focus correctly (widget must be focused)
- Make shortcuts configurable
- Document all available shortcuts
- Consider modal states (e.g., different shortcuts when annotating)

**Tests**:
- Test all default shortcuts
- Test custom shortcut configuration
- Test focus behavior

---

### 3. Multi-Image Curtain (Issue #80)
**Effort**: Medium | **Impact**: Medium | **Timeline**: 2-3 weeks

**Current Limitation**: Curtain only supports 2 images
**Solution**: Extend to support N images with N-1 dividers

**Implementation Steps**:

```python
# Extend _curtain.py
def multi_curtain(images, 
                  orientations=None,
                  slice_number=None,
                  continuous_update=True,
                  **kwargs):
    """
    Display multiple images with adjustable curtain dividers.
    
    Parameters
    ----------
    images : list of ndarray
        List of images to display
    orientations : list of str, optional
        List of 'vertical' or 'horizontal' for each divider
        If None, all dividers are vertical
    """
    import ipywidgets
    from ._image_widget import ImageWidget
    
    n_images = len(images)
    if n_images < 2:
        raise ValueError("Need at least 2 images")
    
    if orientations is None:
        orientations = ['vertical'] * (n_images - 1)
    
    # Create sliders for each divider
    divider_sliders = []
    for i in range(n_images - 1):
        slider = ipywidgets.FloatSlider(
            value=1.0 / n_images * (i + 1),
            min=0,
            max=1,
            step=0.01,
            description=f'Divider {i+1}',
            continuous_update=continuous_update
        )
        divider_sliders.append(slider)
    
    # Composite image based on divider positions
    def create_composite(event=None):
        # Get current slice for all images
        slices = [img[slice_number] if img.ndim > 2 else img 
                  for img in images]
        
        composite = slices[0].copy()
        # Apply each divider in sequence
        # Implementation details depend on orientation
        
        return composite
    
    # Connect sliders to update function
    for slider in divider_sliders:
        slider.observe(create_composite)
```

**Technical Challenges**:
- Efficient compositing of N images
- UI layout for multiple sliders
- Supporting both vertical and horizontal dividers
- Performance with large images

**Tests**:
- Test with 2, 3, 4+ images
- Test mixed orientations
- Test with different image sizes
- Performance test with large images

---

## Medium Effort, High Impact Features

### 4. Measurement Tools
**Effort**: High | **Impact**: High | **Timeline**: 4-6 weeks

**Architecture**:
```
stackview/
  _measurement/
    __init__.py
    _measurement_widget.py      # Main widget
    _measurement_tools.py       # Tool implementations
    _measurement_renderer.py    # Drawing measurements
    _measurement_data.py        # Data structures
```

**Implementation Overview**:

```python
# _measurement_widget.py
class MeasurementWidget:
    def __init__(self, image, tools=None, scale=1.0, units='pixels'):
        self.image = image
        self.scale = scale
        self.units = units
        self.tools = self._init_tools(tools or ['line', 'angle', 'circle'])
        self.measurements = []
        self.active_tool = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Tool buttons
        self.tool_buttons = {
            name: ipywidgets.Button(description=name.title())
            for name in self.tools
        }
        
        # Canvas for drawing
        self.canvas = ImageWidget(self.image)
        
        # Measurement list
        self.measurement_list = ipywidgets.VBox()
        
        # Layout
        self.widget = ipywidgets.VBox([
            ipywidgets.HBox(list(self.tool_buttons.values())),
            self.canvas,
            self.measurement_list
        ])
    
    def add_measurement(self, measurement):
        self.measurements.append(measurement)
        self._update_display()
    
    def get_measurements_df(self):
        import pandas as pd
        return pd.DataFrame([m.to_dict() for m in self.measurements])

# _measurement_tools.py
class LineTool:
    def __init__(self, scale=1.0, units='pixels'):
        self.scale = scale
        self.units = units
        self.start = None
        self.end = None
    
    def on_mouse_down(self, event):
        self.start = (event['relativeX'], event['relativeY'])
    
    def on_mouse_move(self, event):
        if self.start:
            self.end = (event['relativeX'], event['relativeY'])
    
    def on_mouse_up(self, event):
        if self.start and self.end:
            measurement = self.calculate()
            return measurement
    
    def calculate(self):
        import numpy as np
        dx = (self.end[0] - self.start[0]) * self.scale
        dy = (self.end[1] - self.start[1]) * self.scale
        distance = np.sqrt(dx**2 + dy**2)
        return {
            'type': 'line',
            'distance': distance,
            'units': self.units,
            'start': self.start,
            'end': self.end
        }

class AngleTool:
    # Three-point angle measurement
    pass

class CircleTool:
    # Circle/ellipse measurement
    pass
```

**Dependencies**:
- Existing ipyevents for mouse handling
- Consider shapely for geometry calculations

**Features to Include**:
- Line: distance, angle from horizontal
- Angle: 3-point angle measurement
- Circle: area, perimeter, center position
- Polygon: area, perimeter
- Freehand: perimeter, area
- Calibration support
- Export to CSV/DataFrame
- Save/load measurements

---

### 5. 3D Volume Rendering
**Effort**: Very High | **Impact**: High | **Timeline**: 8-12 weeks

**Architecture Decision**: Use ipyvolume vs pythreejs vs custom

**Recommended**: ipyvolume (better integration with jupyter, good performance)

**Implementation**:

```python
# _volume_render.py
def volume_render(image,
                  opacity=0.5,
                  rendering_mode='mip',
                  colormap='viridis',
                  rotate=True,
                  lighting=True,
                  **kwargs):
    """
    3D volume rendering of image stack.
    
    Parameters
    ----------
    image : ndarray
        3D image stack
    opacity : float or ndarray
        Opacity value(s). Can be 1D array for transfer function
    rendering_mode : str
        'mip' (maximum intensity projection),
        'iso' (iso-surface),
        'dvr' (direct volume rendering)
    """
    import ipyvolume as ipv
    import numpy as np
    
    # Prepare data
    if image.ndim != 3:
        raise ValueError("Volume rendering requires 3D data")
    
    # Create figure
    fig = ipv.figure()
    
    if rendering_mode == 'mip':
        # Maximum intensity projection
        ipv.volshow(
            image,
            level=[image.min(), image.max()],
            opacity=opacity,
            controls=rotate
        )
    elif rendering_mode == 'iso':
        # Iso-surface rendering
        from skimage.measure import marching_cubes
        threshold = np.percentile(image, 50)
        verts, faces, normals, values = marching_cubes(image, threshold)
        ipv.plot_trisurf(verts[:, 0], verts[:, 1], verts[:, 2], 
                        triangles=faces, color='cyan')
    
    if lighting:
        ipv.pylab.style.use('light')
    
    ipv.show()
    return fig

# Advanced features
def volume_render_multi_channel(channels, 
                               colors=['red', 'green', 'blue'],
                               opacities=[0.5, 0.5, 0.5]):
    """Render multiple channels with different colors."""
    pass
```

**Technical Challenges**:
- Performance with large volumes
- Memory management
- Downsampling strategies
- Interactive transfer function editing
- Integration with existing stackview API

**Dependencies**:
- ipyvolume or pythreejs
- scikit-image (for marching cubes)

**Progressive Implementation**:
1. Week 1-2: Basic MIP rendering
2. Week 3-4: Iso-surface rendering
3. Week 5-6: Direct volume rendering
4. Week 7-8: Interactive controls
5. Week 9-10: Multi-channel support
6. Week 11-12: Performance optimization

---

### 6. ROI Analysis Tools
**Effort**: High | **Impact**: High | **Timeline**: 6-8 weeks

**Integration with existing tools**: Build on crop and annotate functionality

**Implementation**:

```python
# _roi_analysis.py
class ROIAnalyzer:
    def __init__(self, image, labels=None):
        self.image = image
        self.labels = labels or np.zeros_like(image, dtype=np.uint32)
        self.rois = []
        self.current_roi_id = 1
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Drawing tools
        self.tool_selector = ipywidgets.Dropdown(
            options=['Rectangle', 'Circle', 'Polygon', 'Freehand'],
            description='Tool:'
        )
        
        # Statistics to compute
        self.stats_checkboxes = {
            'mean': ipywidgets.Checkbox(value=True, description='Mean'),
            'std': ipywidgets.Checkbox(value=True, description='Std'),
            'min': ipywidgets.Checkbox(value=False, description='Min'),
            'max': ipywidgets.Checkbox(value=False, description='Max'),
            'sum': ipywidgets.Checkbox(value=False, description='Sum'),
            'area': ipywidgets.Checkbox(value=True, description='Area'),
        }
        
        # Results table
        self.results_output = ipywidgets.Output()
        
        # Image viewer with ROI overlay
        self.viewer = _SliceViewer(self.image)
        
    def add_roi(self, roi_type, coordinates):
        """Add a new ROI."""
        roi = {
            'id': self.current_roi_id,
            'type': roi_type,
            'coordinates': coordinates,
        }
        self.rois.append(roi)
        self.current_roi_id += 1
        
        # Create mask for this ROI
        mask = self._create_mask(roi_type, coordinates)
        self.labels[mask] = roi['id']
        
        # Compute statistics
        self._compute_statistics()
    
    def _create_mask(self, roi_type, coordinates):
        """Create binary mask for ROI."""
        from skimage.draw import polygon, circle, ellipse
        mask = np.zeros(self.image.shape, dtype=bool)
        
        if roi_type == 'Rectangle':
            x, y, w, h = coordinates
            mask[y:y+h, x:x+w] = True
        elif roi_type == 'Circle':
            x, y, r = coordinates
            rr, cc = circle(y, x, r, shape=mask.shape)
            mask[rr, cc] = True
        # ... other shapes
        
        return mask
    
    def _compute_statistics(self):
        """Compute statistics for all ROIs."""
        from skimage.measure import regionprops
        props = regionprops(self.labels, intensity_image=self.image)
        
        results = []
        for prop in props:
            roi_stats = {'roi_id': prop.label}
            
            if self.stats_checkboxes['mean'].value:
                roi_stats['mean'] = prop.mean_intensity
            if self.stats_checkboxes['std'].value:
                roi_stats['std'] = prop.intensity_image[prop.image].std()
            # ... other statistics
            
            results.append(roi_stats)
        
        # Display results
        self._display_results(results)
    
    def get_results_df(self):
        """Export results as pandas DataFrame."""
        import pandas as pd
        return pd.DataFrame(self.results)
    
    def export_rois(self, filename):
        """Export ROI definitions to file."""
        import json
        with open(filename, 'w') as f:
            json.dump(self.rois, f)
```

**Features**:
- Multiple ROI shapes
- ROI manager (list, delete, modify)
- Compute statistics per ROI
- Compare ROIs across slices
- Track ROIs over time
- Export ROI coordinates and statistics
- Import/export ROI definitions

---

## Performance Optimization Strategy

### 7. Large Image Handling
**Effort**: Medium-High | **Impact**: High | **Timeline**: 4-6 weeks

**Current Issues**:
- Slow with large 2D images (Issue #61)
- Memory issues with large stacks
- UI becomes unresponsive

**Solutions**:

#### A. Automatic Downsampling
```python
# Add to _image_widget.py
class ImageWidget(Canvas):
    def __init__(self, image, ..., auto_downsample=True, max_pixels=1000000):
        if auto_downsample:
            total_pixels = image.shape[0] * image.shape[1]
            if total_pixels > max_pixels:
                downsample_factor = np.sqrt(total_pixels / max_pixels)
                image = self._downsample(image, downsample_factor)
                warnings.warn(
                    f"Image downsampled by factor {downsample_factor:.1f} "
                    f"for display. Original resolution preserved for "
                    f"measurements and exports."
                )
```

#### B. Lazy Loading
```python
# _lazy_loader.py
class LazyImageStack:
    def __init__(self, image_source, chunk_size=10):
        self.source = image_source
        self.chunk_size = chunk_size
        self.cache = {}
    
    def __getitem__(self, index):
        if index not in self.cache:
            # Load from disk/memory
            self._load_slice(index)
        return self.cache[index]
    
    def _load_slice(self, index):
        # Load and cache slice
        pass
```

#### C. Dask Integration
```python
# Add dask support
def slice(image, ..., use_dask=None):
    if use_dask is None:
        # Auto-detect dask arrays
        use_dask = 'dask.array' in str(type(image))
    
    if use_dask:
        # Handle dask arrays efficiently
        # Compute slices on demand
        pass
```

#### D. Tiling for Very Large 2D Images
```python
# _tiled_viewer.py
class TiledImageViewer:
    """Viewer for very large 2D images using tiling."""
    def __init__(self, image, tile_size=1024):
        self.image = image
        self.tile_size = tile_size
        self.current_viewport = (0, 0, tile_size, tile_size)
    
    def get_visible_tiles(self):
        """Get only the tiles currently in viewport."""
        pass
```

**Performance Targets**:
- Display images up to 10,000 x 10,000 without lag
- Handle stacks with 1000+ slices
- Memory usage < 2GB for typical workflows
- Smooth interaction (>30 FPS) for navigation

---

## Export and Interoperability

### 8. Advanced Export System
**Effort**: Medium | **Impact**: High | **Timeline**: 3-4 weeks

**Implementation**:

```python
# _export.py
def export(widget, 
           filename,
           dpi=300,
           format=None,
           scalebar=False,
           annotations=True,
           **kwargs):
    """
    Export current view to file.
    
    Formats:
    - PNG, JPEG, TIFF: High-quality images
    - SVG, PDF: Vector graphics (where possible)
    - HTML: Interactive widget
    - MP4, GIF: Animations
    """
    from pathlib import Path
    
    if format is None:
        format = Path(filename).suffix[1:].lower()
    
    if format in ['png', 'jpg', 'jpeg', 'tiff']:
        _export_raster(widget, filename, dpi, **kwargs)
    elif format in ['svg', 'pdf']:
        _export_vector(widget, filename, **kwargs)
    elif format == 'html':
        _export_html(widget, filename, **kwargs)
    elif format in ['mp4', 'gif']:
        _export_animation(widget, filename, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {format}")

def _export_html(widget, filename, standalone=True):
    """Export as standalone HTML with embedded widget."""
    if standalone:
        # Embed all dependencies
        from ipywidgets.embed import embed_minimal_html
        embed_minimal_html(filename, views=[widget])
    else:
        # Require external CDN dependencies
        pass
```

---

## Testing Strategy

### Test Coverage Goals
- Unit tests: >80% coverage
- Integration tests for all major features
- UI/Widget tests where possible
- Performance benchmarks

### Testing Infrastructure

```python
# tests/test_measurement.py
def test_line_measurement():
    image = np.random.rand(100, 100)
    widget = stackview.measure(image)
    
    # Simulate drawing a line
    widget.on_mouse_down({'relativeX': 10, 'relativeY': 10})
    widget.on_mouse_up({'relativeX': 50, 'relativeY': 50})
    
    measurements = widget.get_measurements_df()
    assert len(measurements) == 1
    assert measurements['type'][0] == 'line'
    # Distance should be ~56.5 pixels
    assert 55 < measurements['distance'][0] < 58

# tests/test_performance.py
def test_large_image_performance():
    large_image = np.random.rand(5000, 5000)
    
    import time
    start = time.time()
    widget = stackview.slice(large_image)
    end = time.time()
    
    # Should initialize in less than 1 second
    assert end - start < 1.0
```

---

## Documentation Plan

### 1. API Documentation
- Docstrings for all public functions
- Type hints throughout
- Sphinx documentation

### 2. User Guides
- Getting started tutorial
- Feature guides for each major feature
- Advanced usage patterns
- Troubleshooting guide

### 3. Examples Gallery
- Basic usage examples
- Advanced workflows
- Domain-specific examples (microscopy, medical imaging, etc.)
- Integration examples (ML, cloud, etc.)

### 4. Video Tutorials
- YouTube series covering major features
- Quick tips and tricks
- Workflow demonstrations

---

## Dependency Management

### Current Dependencies
```python
# setup.py - current
install_requires=[
    "numpy!=1.19.4",
    "ipycanvas",
    "ipywidgets",
    "scikit-image",
    "ipyevents",
    "toolz",
    "matplotlib",
    "ipykernel",
    "imageio",
    "ipympl",
    "wordcloud"
]
```

### Proposed Additions
```python
# Core dependencies (required)
install_requires=[
    # ... existing ...
    "matplotlib-scalebar",  # For scalebar feature
]

# Optional dependencies (for specific features)
extras_require={
    'volume': ['ipyvolume>=0.6.0'],
    'performance': ['dask[array]>=2021.0.0'],
    'ml': ['torch>=1.9.0', 'torchvision>=0.10.0'],
    'cloud': ['boto3>=1.20.0', 's3fs>=2021.0.0'],
    'all': ['ipyvolume', 'dask', 'torch', 'boto3'],
}
```

---

## Migration and Compatibility

### Versioning Strategy
- Use semantic versioning
- Major version bump for breaking changes
- Deprecation warnings for at least one minor version

### Backward Compatibility
- Maintain existing API
- New features via optional parameters
- Deprecate gracefully with clear warnings

### Migration Guides
- Document any breaking changes
- Provide migration scripts where possible
- Maintain changelog

---

## Community Contribution Guidelines

### For Contributors
1. Check existing issues and proposals
2. Create issue for discussion before large PRs
3. Follow coding standards (PEP 8, type hints)
4. Add tests for new features
5. Update documentation

### Code Review Process
1. Automated tests must pass
2. Code review by maintainer
3. Documentation review
4. Performance impact assessment

---

## Success Metrics

### Technical Metrics
- Test coverage >80%
- Performance benchmarks met
- No new critical bugs introduced
- Documentation coverage 100%

### User Metrics
- Download statistics
- GitHub stars/forks
- Issue resolution time
- Community contributions

### Qualitative Metrics
- User satisfaction surveys
- Feature adoption rates
- Community engagement (discussions, issues, PRs)

---

## Risk Management

### Technical Risks
1. **Performance degradation**: Mitigation via profiling and optimization
2. **Dependency conflicts**: Use version ranges, test against multiple versions
3. **Browser compatibility**: Test on multiple browsers
4. **Breaking changes in dependencies**: Pin versions, monitor updates

### Process Risks
1. **Scope creep**: Stick to roadmap, defer non-critical features
2. **Resource constraints**: Prioritize ruthlessly
3. **Community expectations**: Communicate clearly and frequently

---

## Conclusion

This roadmap provides a structured approach to implementing the next generation of stackview features. The emphasis is on:

1. **Quick wins first**: Scale bars, keyboard shortcuts deliver immediate value
2. **Solid foundations**: Performance optimization and testing infrastructure
3. **Strategic features**: 3D rendering, measurements, ROI analysis differentiate stackview
4. **Community-driven**: Respond to user needs (Issues #80, #167, #56, #57, etc.)

By following this roadmap, stackview can evolve into the definitive image visualization library for Jupyter notebooks while maintaining its core strengths of simplicity and interactivity.
