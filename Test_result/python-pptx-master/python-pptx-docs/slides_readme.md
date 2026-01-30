Slides
Slides objects
The Slides object is accessed using the slides property of Presentation. It is not intended to be constructed directly.

class pptx.slide.Slides[source]
Sequence of slides belonging to an instance of Presentation.

Has list semantics for access to individual slides. Supports indexed access, len(), and iteration.

add_slide(slide_layout: pptx.slide.SlideLayout) → pptx.slide.Slide[source]
Return a newly added slide that inherits layout from slide_layout.

get(slide_id: int, default: Slide | None = None) → Slide | None[source]
Return the slide identified by int slide_id in this presentation.

Returns default if not found.

index(slide: pptx.slide.Slide) → int[source]
Map slide to its zero-based position in this slide sequence.

Raises ValueError on slide not present.

Slide objects
An individual Slide object is accessed by index from Slides or as the return value of add_slide().

class pptx.slide.Slide[source]
Slide object. Provides access to shapes and slide-level properties.

background
_Background object providing slide background properties.

This property returns a _Background object whether or not the slide, master, or layout has an explicitly defined background.

The same _Background object is returned on every call for the same slide object.

element
The lxml element proxied by this object.

follow_master_background
True if this slide inherits the slide master background.

Assigning False causes background inheritance from the master to be interrupted; if there is no custom background for this slide, a default background is added. If a custom background already exists for this slide, assigning False has no effect.

Assigning True causes any custom background for this slide to be deleted and inheritance from the master restored.

has_notes_slide
True if this slide has a notes slide, False otherwise.

A notes slide is created by notes_slide when one doesn’t exist; use this property to test for a notes slide without the possible side effect of creating one.

name
String representing the internal name of this slide.

Returns an empty string (‘’) if no name is assigned. Assigning an empty string or None to this property causes any name to be removed.

notes_slide
The NotesSlide instance for this slide.

If the slide does not have a notes slide, one is created. The same single instance is returned on each call.

placeholders[source]
Sequence of placeholder shapes in this slide.

shapes[source]
Sequence of shape objects appearing on this slide.

slide_id
Integer value that uniquely identifies this slide within this presentation.

The slide id does not change if the position of this slide in the slide sequence is changed by adding, rearranging, or deleting slides.

slide_layout
SlideLayout object this slide inherits appearance from.

SlideLayouts objects
The SlideLayouts object is accessed using the slide_layouts property of SlideMaster, typically:

>>> from pptx import Presentation
>>> prs = Presentation()
>>> slide_layouts = prs.slide_master.slide_layouts
As a convenience, since most presentations have only a single slide master, the SlideLayouts collection for the first master may be accessed directly from the Presentation object:

>>> slide_layouts = prs.slide_layouts
This class is not intended to be constructed directly.

class pptx.slide.SlideLayouts[source]
Sequence of slide layouts belonging to a slide-master.

Supports indexed access, len(), iteration, index() and remove().

get_by_name(name: str, default: SlideLayout | None = None) → SlideLayout | None[source]
Return SlideLayout object having name, or default if not found.

index(slide_layout: pptx.slide.SlideLayout) → int[source]
Return zero-based index of slide_layout in this collection.

Raises ValueError if slide_layout is not present in this collection.

part
The package part containing this object.

remove(slide_layout: pptx.slide.SlideLayout) → None[source]
Remove slide_layout from the collection.

Raises ValueError when slide_layout is in use; a slide layout which is the basis for one or more slides cannot be removed.

SlideLayout objects
class pptx.slide.SlideLayout(element: BaseOxmlElement, part: XmlPart)[source]
Slide layout object.

Provides access to placeholders, regular shapes, and slide layout-level properties.

placeholders[source]
Sequence of placeholder shapes in this slide layout.

Placeholders appear in idx order.

shapes[source]
Sequence of shapes appearing on this slide layout.

slide_master
Slide master from which this slide-layout inherits properties.

used_by_slides
Tuple of slide objects based on this slide layout.

SlideMasters objects
The SlideMasters object is accessed using the slide_masters property of Presentation, typically:

>>> from pptx import Presentation
>>> prs = Presentation()
>>> slide_masters = prs.slide_masters
As a convenience, since most presentations have only a single slide master, the first master may be accessed directly from the Presentation object without indexing the collection:

>>> slide_master = prs.slide_master
This class is not intended to be constructed directly.

class pptx.slide.SlideMasters[source]
Sequence of SlideMaster objects belonging to a presentation.

Has list access semantics, supporting indexed access, len(), and iteration.

part
The package part containing this object.

SlideMaster objects
class pptx.slide.SlideMaster(element: BaseOxmlElement, part: XmlPart)[source]
Slide master object.

Provides access to slide layouts. Access to placeholders, regular shapes, and slide master-level properties is inherited from _BaseMaster.

slide_layouts[source]
SlideLayouts object providing access to this slide-master’s layouts.

SlidePlaceholders objects
class pptx.shapes.shapetree.SlidePlaceholders(element: BaseOxmlElement, parent: ProvidesPart)[source]
Collection of placeholder shapes on a slide.

Supports iteration, len(), and dictionary-style lookup on the idx value of the placeholders it contains.

NotesSlide objects
class pptx.slide.NotesSlide(element: BaseOxmlElement, part: XmlPart)[source]
Notes slide object.

Provides access to slide notes placeholder and other shapes on the notes handout page.

background
_Background object providing slide background properties.

This property returns a _Background object whether or not the slide, master, or layout has an explicitly defined background.

The same _Background object is returned on every call for the same slide object.

element
The lxml element proxied by this object.

name
String representing the internal name of this slide.

Returns an empty string (‘’) if no name is assigned. Assigning an empty string or None to this property causes any name to be removed.

notes_placeholder
the notes placeholder on this notes slide, the shape that contains the actual notes text.

Return None if no notes placeholder is present; while this is probably uncommon, it can happen if the notes master does not have a body placeholder, or if the notes placeholder has been deleted from the notes slide.

notes_text_frame
The text frame of the notes placeholder on this notes slide.

None if there is no notes placeholder. This is a shortcut to accommodate the common case of simply adding “notes” text to the notes “page”.

part
The package part containing this object.

placeholders[source]
Instance of NotesSlidePlaceholders for this notes-slide.

Contains the sequence of placeholder shapes in this notes slide.

shapes[source]
Sequence of shape objects appearing on this notes slide.