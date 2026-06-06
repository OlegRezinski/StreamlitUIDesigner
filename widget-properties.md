# Widget Properties

This document lists the properties shown in the Properties pane for each widget in the widget palette.

## Button

Display a button widget. This replaces the legacy Button section at the top of this file.

Function signature
    st.button(label, key=None, help=None, on_click=None, args=None, kwargs=None, *, type="secondary", icon=None, icon_position="left", disabled=False, use_container_width=None, width="content", shortcut=None)

label (str)

    Default: "Button"
    The label displayed on the button.
    In properties pane: text field.
    Always generate in code as the first positional argument.
    The label can optionally contain GitHub-flavored Markdown of the following types: Bold, Italics, Strikethroughs, Inline Code, Links, and Images.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

help (str or None)

    Default: None (empty string in pane)
    A tooltip that gets displayed when the button is hovered over. If this is None (default), no tooltip is displayed.
    Generate in code only if non-empty.

type ("primary", "secondary", or "tertiary")

    Default: "secondary"
    In properties pane should be a selectbox with options "primary", "secondary", and "tertiary".

    An optional string that specifies the button type. This can be one of the following:

    "primary": The button's background is the app's primary color for additional emphasis.
    "secondary" (default): The button's background coordinates with the app's background color for normal emphasis.
    "tertiary": The button is plain text without a border or background for subtlety.

icon (str or None)

    Default: "" (None)
    In properties pane: text field.
    An optional emoji or icon to display next to the button label. If empty, no icon is displayed and icon is not emitted in code.
    Accepted formats:
    - A single-character emoji. For example, "🚨" or "🔥". Emoji short codes are not supported.
    - An icon from the Material Symbols library (rounded style) in the format ":material/icon_name:" where "icon_name" is the name of the icon in snake case.
    - "spinner": Displays a spinner as an icon.
    Generate in code only if non-empty.

icon_position ("left" or "right")

    Default: "left"
    Should not be displayed in properties pane.
    Generate in code only when icon is non-empty; use default value "left".

disabled (bool)

    Default: False
    In properties pane: checkbox with default value False.
    Generate in code only if True.

width ("content", "stretch", or "custom")

    The width of the button element. This can be one of the following:

    "content" (default): The width of the button matches the width of its content, but doesn't exceed the width of the parent container.
    "stretch": The width of the button matches the width of the parent container.
    "custom": The width of the button is specified by the custom width property.

    In properties pane: selectbox with options "content", "stretch", "custom".

custom width (int)

    Default: 200
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The button has a fixed width. If the specified width is greater than the width of the parent container, the width of the button matches the width of the parent container.

background_color (colorpicker)

    Default: "" (no custom color)
    In properties pane: color picker.
    When empty (default), no custom background color is applied — the button uses its native Streamlit type styling.
    When set to a hex color value (e.g. "#FF5733"), inject a CSS <style> block after the button to override the button's background color.
    The CSS targets the button via its key using the `.st-key-{key} button` selector.
    Generate in code only if non-empty.

text_color (colorpicker)

    Default: "" (no custom color)
    In properties pane: color picker.
    When empty (default), no custom text color is applied — the button uses its native Streamlit type styling.
    When set to a hex color value (e.g. "#FFFFFF"), inject a CSS <style> block after the button to override the button's text color.
    The CSS targets the button via its key using the `.st-key-{key} button` selector.
    Generate in code only if non-empty.

on_click, args, kwargs

    Should not be displayed in properties pane. Not generated in code.

use_container_width

    Deprecated. Should not be displayed in properties pane. Not generated in code.

shortcut (str or None)

    Should not be displayed in properties pane. Not generated in code.




## Checkbox
- Label
- Checked
- Disabled
- Label visible

## Color picker
- Label
- Color (hex)

## Columns container
- Label
- Background color
- Columns

## Date input
- Label
- Date (YYYY-MM-DD)

## File uploader
- Label
- File types (comma separated)

## Multiselect
- Label
- Options (comma separated)
- Default (comma separated)

## Number input
- Label
- Min
- Max
- Value
- Step

## Radio
- Label
- Options (comma separated)
- Selected index

## Selectbox
- Label
- Options (comma separated)
- Selected index

## Slider
- Label
- Min
- Max
- Value
- Step

## Text
- Text
- Size
- Color
- Horizontal alignment
- Vertical alignment
- Style
- Bold
- Italic

## Title
- Text
- Size
- Color
- Horizontal alignment
- Style
- Bold
- Italic

## Header
- Text
- Size
- Color
- Horizontal alignment
- Vertical alignment
- Style
- Bold
- Italic

## Subheader
- Text
- Size
- Color
- Horizontal alignment
- Vertical alignment
- Style
- Bold
- Italic

## Markdown
- Text
- Size
- Color
- Horizontal alignment
- Vertical alignment
- Style
- Bold
- Italic

## Badge
- Text
- Size
- Text color
- Background color
- Horizontal alignment
- Vertical alignment
- Style
- Bold
- Italic

## Caption
- Text
- Size
- Color
- Horizontal alignment
- Vertical alignment
- Style
- Bold
- Italic

## Code
- Width (`content` / `stretch`)
- Height (`content` / `stretch`)

## Text area
- Label
- Default value

## Text input
- Label
- Default value

## Divider
- Line width
- Color

## Echo
- Code location (`above` / `below`)

## Latex
- Text
- Help
- Width (`stretch` / `content` / `custom`)
- Custom width (int)
- Font size

## Toggle
- Label
- On

## Help
- Text
- Width (`stretch` / `custom`)
- Custom width (int)

## DataFrame
- Width (`stretch` / `content` / `custom`)
- Custom width (int)
- Height (`auto` / `stretch` / `content` / `custom`)
- Custom height
- Selection mode (`single-row`, `multi-row`, `single-column`, `multi-column`, `single-cell`, `multi-cell`)
- Hide index (bool)
- Row height (int or None)

## DataEditor
- Width (`stretch` / `content` / `custom`)
- Custom width (int)
- Height (`auto` / `stretch` / `content` / `custom`)
- Custom height
- Hide index (bool)
- Num rows (`fixed`/ `dynamic`/ `add`/ `delete`)
- Row height (int or None)
- Disabled (`False` / `True`)

## Table
- Width (`stretch` / `content` / `custom`)
- Custom width (int)
- Height (`auto` / `stretch` / `content` / `custom`)
- Custom height
- Border - selectbox with options True/False/"horizontal"

## Metric
label (str)

    The header or title for the metric. The label can optionally contain GitHub-flavored Markdown of the following types: Bold, Italics, Strikethroughs, Inline Code, Links, and Images. Images display like icons, with a max height equal to the font height.
    
    Unsupported Markdown elements are unwrapped so only their children (text contents) render. Common block-level Markdown (headings, lists, blockquotes) is automatically escaped and displays as literal text in labels.
    
    See the body parameter of st.markdown for additional, supported Markdown directives.
    
    value (int, float, decimal.Decimal, str, or None)
    
    Value of the metric. None is rendered as a long dash.
    
    The value can optionally contain GitHub-flavored Markdown, subject to the same limitations described in the label parameter.

delta (int, float, decimal.Decimal, str, or None)
    
    Amount or indicator of change in the metric. An arrow is shown next to the delta, oriented according to its sign:
    
    If the delta is None or an empty string, no arrow is shown.
    If the delta is a negative number or starts with a minus sign, the arrow points down and the delta is red.
    Otherwise, the arrow points up and the delta is green.
    You can modify the display, color, and orientation of the arrow using the delta_color and delta_arrow parameters.
    
    The delta can optionally contain GitHub-flavored Markdown, subject to the same limitations described in the label parameter.

delta_color (str)

    The color of the delta and chart. This can be one of the following:
    
    "normal" (default): The color is red when the delta is negative and green otherwise.
    "inverse": The color is green when the delta is negative and red otherwise. This is useful when a negative change is considered good, like a decrease in cost.
    "off": The color is gray regardless of the delta.
    A named color from the basic palette: The chart and delta are the specified color regardless of their value. This can be one of the following: "red", "orange", "yellow", "green", "blue", "violet", "gray"/"grey", or "primary".

help (str or None)

    A tooltip that gets displayed next to the metric label. Streamlit only displays the tooltip when label_visibility="visible". If this is None (default), no tooltip is displayed.
    
    The tooltip can optionally contain GitHub-flavored Markdown, including the Markdown directives described in the body parameter of st.markdown.

label_visibility ("visible", "hidden", or "collapsed")

    The visibility of the label. The default is "visible". If this is "hidden", Streamlit displays an empty spacer instead of the label, which can help keep the widget aligned with other widgets. If this is "collapsed", Streamlit displays no label or spacer.

border (bool)

    Whether to show a border around the metric container. If this is False (default), no border is shown. If this is True, a border is shown.

background_color (colorpicker)
.

    Background color for the metric card container.

height ("content", "stretch", or int)

    The height of the metric element. This can be one of the following:
    
    "content" (default): The height of the element matches the height of its content.
    "stretch": The height of the element matches the height of its content or the height of the parent container, whichever is larger. If the element is not in a parent container, the height of the element matches the height of its content.
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled.

width ("stretch", "content", or int)

    The width of the metric element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

chart_data (Iterable or None)

    A sequence of numeric values to display as a sparkline chart. If this is None (default), no chart is displayed. The sequence can be anything supported by st.dataframe, including a list or set. If the sequence is dataframe-like, the first column will be used. Each value will be cast to float internally by default.
    
    The chart uses the color of the delta indicator, which can be modified using the delta_color parameter.

chart_type ("line", "bar", or "area")

    The type of sparkline chart to display. This can be one of the following:
    
    "line" (default): A simple sparkline.
    "area": A sparkline with area shading.
    "bar": A bar chart.

delta_arrow ("auto", "up", "down", or "off")

    Controls the direction of the delta indicator arrow. This can be one of the following strings:
    
    "auto" (default): The arrow direction follows the sign of delta.
    "up" or "down": The arrow is forced to point in the specified direction.
    "off": No arrow is shown, but the delta value remains visible.

format (str or None) - selectbox

    A format string controlling how numbers are displayed for value and delta. The format is only applied if the value or delta is numeric. If the value or delta is a string with non-numeric characters, the format is ignored. The format can be one of the following values:
    
    None (default): No formatting is applied.
    "plain": Show the full number without any formatting (e.g. "1234.567").
    "localized": Show the number in the default locale format (e.g. "1,234.567").
    "percent": Show the number as a percentage (e.g. "123456.70%").
    "dollar": Show the number as a dollar amount (e.g. "$1,234.57").
    "euro": Show the number as a euro amount (e.g. "€1,234.57").
    "yen": Show the number as a yen amount (e.g. "¥1,235").
    "accounting": Show the number in an accounting format (e.g. "1,234.00").
    "bytes": Show the number in a byte format (e.g. "1.2KB").
    "compact": Show the number in a compact format (e.g. "1.2K").
    "scientific": Show the number in scientific notation (e.g. "1.235E3").
    "engineering": Show the number in engineering notation (e.g. "1.235E3").
    printf-style format string: Format the number with a printf specifier, like "%d" to show a signed integer (e.g. "1234") or "%.2f" to show a float with 2 decimal places. Use , for thousand separators (e.g. "%,d" yields "1,234").

delta_description (str or None)

    A short description displayed next to the delta value, such as "month over month" or "vs. last quarter". If this is None (default), no description is shown. The description is displayed in a smaller, muted font style similar to st.caption.

## Json
Display an object or string as a pretty-printed, interactive JSON string.

expanded (bool or "custom")

    The initial expansion state of the JSON element. This can be one of the following:

    True (default): The element is fully expanded.
    False: The element is fully collapsed.
    An integer: The element is expanded to the depth specified. The integer must be non-negative. expanded=0 is equivalent to expanded=False.
    Regardless of the initial expansion state, users can collapse or expand any key-value pair to show or hide any part of the object.

custom expanded (int)

    If Expaned selection is not "custom", disabled.
    If Expaned selection is "custom", the input must be an integer,
    The element is expanded to the depth specified. The integer must be non-negative. expanded=0 is equivalent to expanded=False.
    Regardless of the initial expansion state, users can collapse or expand any key-value pair to show or hide any part of the object.

width ("stretch", "contain" or "custom")

    The width of the JSON element. This can be one of the following:

    "stretch" (default): The width of the element matches the width of the parent container.
    
custom width (Integer)

    if width selection is not "custom" - disabled else 
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.


## Area chart

Display an area chart.
This is syntax-sugar around st.altair_chart. The main difference is this command uses the data's own column and indices to figure out the chart's Altair spec. As a result this is easier to use for many "just plot this" scenarios, while being less customizable.


x_label (str or None)

    The label for the x-axis. If this is None (default), Streamlit will use the column name specified in x if available, or else no label will be displayed.

y_label (str or None)

    The label for the y-axis. If this is None (default), Streamlit will use the column name(s) specified in y if available, or else no label will be displayed.

stack (bool, "normalize", "center", or None)

    Whether to stack the areas. If this is None (default), Streamlit uses Vega's default. Other values can be as follows:
    
    True: The areas form a non-overlapping, additive stack within the chart.
    False: The areas overlap each other without stacking.
    "normalize": The areas are stacked and the total height is normalized to 100% of the height of the chart.
    "center": The areas are stacked and shifted to center their baseline, which creates a steamgraph.

width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.

custom width (int)

    disabled if width property is not "custom" else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.
    
height ("stretch", "content" or "custom")

    The height of the chart element. This can be one of the following:
    
    "content" (default): The height of the element matches the height of its content.
    "stretch": The height of the element matches the height of its content or the height of the parent container, whichever is larger. If the element is not in a parent container, the height of the element matches the height of its content.

custom height (int):
    
    disabled if height property is not "custom" else enabled.
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled.


## Bar chart

Display a bar chart.
This is syntax-sugar around st.altair_chart. The main difference is this command uses the data's own column and indices to figure out the chart's Altair spec. As a result this is easier to use for many "just plot this" scenarios, while being less customizable.

x_label (str or None)

    The label for the x-axis. If this is None (default), Streamlit will use the column name specified in x if available, or else no label will be displayed.

y_label (str or None)

    The label for the y-axis. If this is None (default), Streamlit will use the column name(s) specified in y if available, or else no label will be displayed.

horizontal (bool)

    Whether to make the bars horizontal. If this is False (default), the bars display vertically. If this is True, Streamlit swaps the x-axis and y-axis and the bars display horizontally.

sort (bool or str)

    How to sort the bars. This can be one of the following:

    True (default): The bars are sorted automatically along the independent/categorical axis with Altair's default sorting. This also correctly sorts ordered categorical columns (pd.Categorical).
    False: The bars are shown in data order without sorting.
    The name of a column (e.g. "col1"): The bars are sorted by that column in ascending order.
    The name of a column with a minus-sign prefix (e.g. "-col1"): The bars are sorted by that column in descending order.
stack (bool, "normalize", "center", "layered", or None)

    Whether to stack the bars. If this is None (default), Streamlit uses Vega's default. Other values can be as follows:
    
    True: The bars form a non-overlapping, additive stack within the chart.
    False: The bars display side by side.
    "layered": The bars overlap each other without stacking.
    "normalize": The bars are stacked and the total height is normalized to 100% of the height of the chart.
    "center": The bars are stacked and shifted to center the total height around an axis.

width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:

    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.

custom width (int):

    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

height ("stretch", "content", or "custom)

    The height of the chart element. This can be one of the following:
    
    "content" (default): The height of the element matches the height of its content.
    "stretch": The height of the element matches the height of its content or the height of the parent container, whichever is larger. If the element is not in a parent container, the height of the element matches the height of its content.

custom height (int):

    if height property is not set to "custom" - disabled, else enabled.
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled.


## Line chart

Display a line chart.

This is syntax-sugar around st.altair_chart. The main difference is this command uses the data's own column and indices to figure out the chart's Altair spec. As a result this is easier to use for many "just plot this" scenarios, while being less customizable.

x_label (str or None)

    The label for the x-axis. If this is None (default), Streamlit will use the column name specified in x if available, or else no label will be displayed.

y_label (str or None)

    The label for the y-axis. If this is None (default), Streamlit will use the column name(s) specified in y if available, or else no label will be displayed.

width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.

custom width (int)
    
    if width property is not set to "custom" - disabled, else enabled.

    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

height ("stretch", "content", or "custom)

    The height of the chart element. This can be one of the following:
    
    "content" (default): The height of the element matches the height of its content.
    "stretch": The height of the element matches the height of its content or the height of the parent container, whichever is larger. If the element is not in a parent container, the height of the element matches the height of its content.

custom height (int):

    if height property is not set to "custom" - disabled, else enabled.
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled.

## Map

    Display a map with a scatterplot overlaid onto it.
    
    This is a wrapper around st.pydeck_chart to quickly create scatterplot charts on top of a map, with auto-centering and auto-zoom.
    
    When using this command, a service called Carto provides the map tiles to render map content. If you're using advanced PyDeck features you may need to obtain an API key from Carto first. You can do that as pydeck.Deck(api_keys={"carto": YOUR_KEY}) or by setting the CARTO_API_KEY environment variable. See PyDeck's documentation for more information.
    
    Another common provider for map tiles is Mapbox. If you prefer to use that, you'll need to create an account at https://mapbox.com and specify your Mapbox key when creating the pydeck.Deck object. You can do that as pydeck.Deck(api_keys={"mapbox": YOUR_KEY}) or by setting the MAPBOX_API_KEY environment variable.
    
    Carto and Mapbox are third-party products and Streamlit accepts no responsibility or liability of any kind for Carto or Mapbox, or for any content or information made available by Carto or Mapbox. The use of Carto or Mapbox is governed by their respective Terms of Use.
    
    Function signature[source]
    st.map(data=None, *, latitude=None, longitude=None, color=None, size=None, zoom=None, width="stretch", height=500, use_container_width=None)
    
    Parameters
    data (Anything supported by st.dataframe)
    
    The data to be plotted.
    
    latitude (str or None)
    
    The name of the column containing the latitude coordinates of the datapoints in the chart.
    
    If None, the latitude data will come from any column named 'lat', 'latitude', 'LAT', or 'LATITUDE'.
    
    longitude (str or None)
    
    The name of the column containing the longitude coordinates of the datapoints in the chart.
    
    If None, the longitude data will come from any column named 'lon', 'longitude', 'LON', or 'LONGITUDE'.
    
    color (str or tuple or None)
    
    The color of the circles representing each datapoint.
    
    Can be:
    
    None, to use the default color.
    A hex string like "#ffaa00" or "#ffaa0088".
    An RGB or RGBA tuple with the red, green, blue, and alpha components specified as ints from 0 to 255 or floats from 0.0 to 1.0.
    The name of the column to use for the color. Cells in this column should contain colors represented as a hex string or color tuple, as described above.
    size (str or float or None)

    The size of the circles representing each point, in meters.
    
    This can be:
    
    None, to use the default size.
    A number like 100, to specify a single size to use for all datapoints.
    The name of the column to use for the size. This allows each datapoint to be represented by a circle of a different size.
    zoom (int)
    
    Zoom level as specified in https://wiki.openstreetmap.org/wiki/Zoom_levels.
    
    width ("stretch" or int)
    
    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.
    height ("stretch" or int)
    
    The height of the chart element. This can be one of the following:
    
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled. This is 500 by default.
    "stretch": The height of the element matches the height of its content or the height of the parent container, whichever is larger. If the element is not in a parent container, the height of the element matches the height of its content.
    use_container_width (bool or None)
    
    delete
    use_container_width is deprecated and will be removed in a future release. For use_container_width=True, use width="stretch".
    
    Whether to override the map's native width with the width of the parent container. This can be one of the following:
    
    None (default): Streamlit will use the map's default behavior.
    True: Streamlit sets the width of the map to match the width of the parent container.
    False: Streamlit sets the width of the map to fit its contents according to the plotting library, up to the width of the parent container.

latitude (str or None)

    The name of the column containing the latitude coordinates of the datapoints in the chart.

    If None, the latitude data will come from any column named 'lat', 'latitude', 'LAT', or 'LATITUDE'.

longitude (str or None)

    The name of the column containing the longitude coordinates of the datapoints in the chart.
    
    If None, the longitude data will come from any column named 'lon', 'longitude', 'LON', or 'LONGITUDE'.

size (str or float or None)

    The size of the circles representing each point, in meters.
    
    This can be:
    
    None, to use the default size.
    A number like 100, to specify a single size to use for all datapoints.
    The name of the column to use for the size. This allows each datapoint to be represented by a circle of a different size.

zoom (int)

    Zoom level as specified in https://wiki.openstreetmap.org/wiki/Zoom_levels.

width ("stretch" or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.

custom width (int)
    
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

height ("stretch" or "custom")

    The height of the chart element. This can be one of the following:

custom height (int):

    if height property is not set to "custom" - disabled, else enabled.
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled.


## Scatter chart

Display a scatterplot chart.

This is syntax-sugar around st.altair_chart. The main difference is this command uses the data's own column and indices to figure out the chart's Altair spec. As a result this is easier to use for many "just plot this" scenarios, while being less customizable.


x_label (str or None)

    The label for the x-axis. If this is None (default), Streamlit will use the column name specified in x if available, or else no label will be displayed.

y_label (str or None)

    The label for the y-axis. If this is None (default), Streamlit will use the column name(s) specified in y if available, or else no label will be displayed.

size (str or float or None)

    The size of the circles representing each point.
    This can be:
    A number like 100, to specify a single size to use for all datapoints.
    The name of the column to use for the size. This allows each datapoint to be represented by a circle of a different size.


width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.

custom width (int)
    
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

height ("stretch", "content", or "custom")

    The height of the chart element. This can be one of the following:
    
    "content" (default): The height of the element matches the height of its content.
    "stretch": The height of the element matches the height of its content or the height of the parent container, whichever is larger. If the element is not in a parent container, the height of the element matches the height of its content.

custom height (int):

    if height property is not set to "custom" - disabled, else enabled.
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled.


## Graphviz chart

Display a graph using the dagre-d3 library.

width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.

custom width (int)
    
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

height ("stretch", "content", or "custom")

    The height of the chart element. This can be one of the following:
    
    "content" (default): The height of the element matches the height of its content.
    "stretch": The height of the element matches the height of its content or the height of the parent container, whichever is larger. If the element is not in a parent container, the height of the element matches the height of its content.

custom height (int):

    if height property is not set to "custom" - disabled, else enabled.
    An integer specifying the height in pixels: The element has a fixed height. If the content is larger than the specified height, scrolling is enabled.


## Download button

Display a download button widget.
This is useful when you would like to provide a way for your users to download a file directly from your app.
If you pass the data directly to the data parameter, then the data is stored in-memory while the user is connected. It's a good idea to keep file sizes under a couple hundred megabytes to conserve memory or use deferred data generation by passing a callable to the data parameter.
If you want to prevent your app from rerunning when a user clicks the download button, wrap the download button in a fragment.

label (str):
    
    Default: "Download"

    A short label explaining to the user what this button is for. The label can optionally contain GitHub-flavored Markdown of the following types: Bold, Italics, Strikethroughs, Inline Code, Links, and Images. Images display like icons, with a max height equal to the font height.
    Unsupported Markdown elements are unwrapped so only their children (text contents) render. Common block-level Markdown (headings, lists, blockquotes) is automatically escaped and displays as literal text in labels.
    See the body parameter of st.markdown for additional, supported Markdown directives.

data (str, bytes, file-like, or callable):
    
    Default: "Your data goes here"

    Don't create in properties pane. generate in code with default value.

    The contents of the file to be downloaded or a callable that returns the contents of the file.
    File contents can be a string, bytes, or file-like object. File-like objects include io.BytesIO, io.StringIO, or any class that implements the abstract base class io.RawIOBase.
    
    If a callable is passed, it is executed when the user clicks the download button and runs on a separate thread from the resulting script rerun. This deferred generation is helpful for large files to avoid blocking the page script. The callable can't accept any arguments. If any Streamlit commands are executed inside the callable, they will be ignored.
    
    To prevent unnecessary recomputation, use caching when converting your data for download. For more information, see the Example 1 below.

file_name (str):
    
    Default: "Your_file_name.txt"

    An optional string to use as the name of the file to be downloaded, such as "my_file.csv". If not specified, the name will be automatically generated.

mime (str or None)

    Default: None
    
    Don't create in properties pane. generate in code with default value.

    The MIME type of the data. If this is None (default), Streamlit sets the MIME type depending on the value of data as follows:
    
    If data is a string or textual file (i.e. str or io.TextIOWrapper object), Streamlit uses the "text/plain" MIME type.
    If data is a binary file or bytes (i.e. bytes, io.BytesIO, io.BufferedReader, or io.RawIOBase object), Streamlit uses the "application/octet-stream" MIME type.
    For more information about MIME types, see https://www.iana.org/assignments/media-types/media-types.xhtml.

key (str, int, or None)

    An optional string or integer to use as the unique key for the widget. If this is None (default), a key will be generated for the widget based on the values of the other parameters. No two widgets may have the same key. Assigning a key stabilizes the widget's identity and preserves its state across reruns even when other parameters change.
    A key lets you access the widget's value via st.session_state[key] (read-only). For more details, see Widget behavior.
    Additionally, if key is provided, it will be used as a CSS class name prefixed with st-key-.
    inproperties pane display generated key, if key is changed apply the change to generated code as well.

help (str or None)
    
    Default:  None  

    A tooltip that gets displayed when the button is hovered over. If this is None (default), no tooltip is displayed.
    The tooltip can optionally contain GitHub-flavored Markdown, including the Markdown directives described in the body parameter of st.markdown.

type ("primary", "secondary", or "tertiary")
    
    Default: "secondary"
    
    In properties pane should be a selectbox with options "primary", "secondary", and "tertiary". The default value is "secondary".

    An optional string that specifies the button type. This can be one of the following:

    "primary": The button's background is the app's primary color for additional emphasis.
    "secondary" (default): The button's background coordinates with the app's background color for normal emphasis.
    "tertiary": The button is plain text without a border or background for subtlety.tip can optionally contain GitHub-flavored Markdown, including the Markdown directives described in the body parameter of st.markdown.

icon (str or None)
    
    Default: None
    
    Should not be diplayed in properties pane, generate in code with ":material/download:" as icon.

    An optional emoji or icon to display next to the button label. If icon is None (default), no icon is displayed. If icon is a string, the following options are valid:
    A single-character emoji. For example, you can set icon="🚨" or icon="🔥". Emoji short codes are not supported.
    An icon from the Material Symbols library (rounded style) in the format ":material/icon_name:" where "icon_name" is the name of the icon in snake case.
    For example, icon=":material/thumb_up:" will display the Thumb Up icon. Find additional icons in the Material Symbols font library.
    "spinner": Displays a spinner as an icon.

icon_position ("left" or "right")
    
    Default: "left"

    Should not be diplayed in properties pane, generate in code with default value.

    The position of the icon relative to the button label. This defaults to "left".

disabled (bool)

    Default:  False  
    
    In properties pane display as a checkbox with default value False.

    An optional boolean that disables the download button if set to True. The default is False.

width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.

custom width (int)
    
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.


## Link button

Display a link button element.
When clicked, a new tab will be opened to the specified URL. This will create a new session for the user if directed within the app.

label (str)

    A short label explaining to the user what this button is for. The label can optionally contain GitHub-flavored Markdown of the following types: Bold, Italics, Strikethroughs, Inline Code, Links, and Images. Images display like icons, with a max height equal to the font height.
    Unsupported Markdown elements are unwrapped so only their children (text contents) render. Common block-level Markdown (headings, lists, blockquotes) is automatically escaped and displays as literal text in labels.
    See the body parameter of st.markdown for additional, supported Markdown directives.

url (str)

    The URL to open on user click.
    
    Default: "https://www.streamlit.io"
    
    Generate code with default values


help (str or None)
    
    Default:  None  

    A tooltip that gets displayed when the button is hovered over. If this is None (default), no tooltip is displayed.
    The tooltip can optionally contain GitHub-flavored Markdown, including the Markdown directives described in the body parameter of st.markdown.

type ("primary", "secondary", or "tertiary")
    
    Default: "secondary"
    
    In properties pane should be a selectbox with options "primary", "secondary", and "tertiary". The default value is "secondary".

    An optional string that specifies the button type. This can be one of the following:

    "primary": The button's background is the app's primary color for additional emphasis.
    "secondary" (default): The button's background coordinates with the app's background color for normal emphasis.
    "tertiary": The button is plain text without a border or background for subtlety.tip can optionally contain GitHub-flavored Markdown, including the Markdown directives described in the body parameter of st.markdown.

icon (str or None)
    
    Default: None
    
    Should not be diplayed in properties pane, generate in code with ":material/download:" as icon.

    An optional emoji or icon to display next to the button label. If icon is None (default), no icon is displayed. If icon is a string, the following options are valid:
    A single-character emoji. For example, you can set icon="🚨" or icon="🔥". Emoji short codes are not supported.
    An icon from the Material Symbols library (rounded style) in the format ":material/icon_name:" where "icon_name" is the name of the icon in snake case.
    For example, icon=":material/thumb_up:" will display the Thumb Up icon. Find additional icons in the Material Symbols font library.
    "spinner": Displays a spinner as an icon.

icon_position ("left" or "right")
    
    Default: "left"

    Should not be diplayed in properties pane, generate in code with default value.

    The position of the icon relative to the button label. This defaults to "left".

disabled (bool)

    Default:  False  
    
    In properties pane display as a checkbox with default value False.

    An optional boolean that disables the download button if set to True. The default is False.

width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

custom width (int)
    
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

## Page link

Display a link to another page in a multipage app or to an external page.
If another page in a multipage app is specified, clicking st.page_link stops the current page execution and runs the specified page as if the user clicked on it in the sidebar navigation.
If an external page is specified, clicking st.page_link opens a new tab to the specified page. The current script run will continue if not complete.
All properties that are in the function signature should be generated with in st.page_link and not in st.markdown.

Function signature
    st.page_link(page, *, label=None, icon=None, icon_position="left", help=None, disabled=False, use_container_width=None, width="content", query_params=None)



page (str, Path, or StreamlitPage)
    
    Default: "https://www.streamlit.io"
    When generating code, use default value.

    The page to switch to on user click. This can be one of the following values:
    Path to a Python file: The path can be a string or pathlib.Path object. It can be absolute or relative to the entrypoint file. The Python file must be the source of a page in st.navigation.
    If you are using the pages/ directory instead of st.navigation, the Python file must be your entrypoint file or a file in the pages/ directory.
    StreamlitPage: The source of the StreamlitPage and its url_path must match a page defined in st.navigation. Use st.Page to create a StreamlitPage object.
    URL: The URL must contain an HTTP or HTTPS scheme, like "https://docs.streamlit.io". When a user clicks a URL-defined page link, the URL opens in a new tab and the app doesn't rerun. If the page link is defined by a URL, then the label parameter is required.
    To link to a page defined by a callable, you must use a StreamlitPage object.

label (str)

    Default: "Page link"
    When generating code, use default value.

    The label for the page link. Labels are required for external pages. The label can optionally contain GitHub-flavored Markdown of the following types: Bold, Italics, Strikethroughs, Inline Code, Links, and Images. Images display like icons, with a max height equal to the font height.
    Unsupported Markdown elements are unwrapped so only their children (text contents) render. Common block-level Markdown (headings, lists, blockquotes) is automatically escaped and displays as literal text in labels.
    See the body parameter of st.markdown for additional, supported Markdown directives.

icon (str or None)
    
    Default: ":material/thumb_up:"
    Should not be diplayed in properties pane, generate in code with default value.
    
    An optional emoji or icon to display next to the link label. If icon is None (default), the icon is inferred from the StreamlitPage object or no icon is displayed. If icon is a string, the following options are valid:
    A single-character emoji. For example, you can set icon="🚨" or icon="🔥". Emoji short codes are not supported.
    An icon from the Material Symbols library (rounded style) in the format ":material/icon_name:" where "icon_name" is the name of the icon in snake case.
    For example, icon=":material/thumb_up:" will display the Thumb Up icon. Find additional icons in the Material Symbols font library.
    "spinner": Displays a spinner as an icon.

icon_position ("left" or "right")
    
    Default: "left"
    Should not be diplayed in properties pane, generate in code with default value.
    The position of the icon relative to the link label. This defaults to "left".

help (str or None)
    
    Default: None
    Generate code with default value.
    A tooltip that gets displayed when the link is hovered over. If this is None (default), no tooltip is displayed.
    The tooltip can optionally contain GitHub-flavored Markdown, including the Markdown directives described in the body parameter of st.markdown.
    disabled (bool)
    An optional boolean that disables the page link if set to True. The default is False.   
    
disabled (bool)

    Default:  False  
    
    In properties pane display as a checkbox with default value False.

    An optional boolean that disables the download button if set to True. The default is False.



width ("stretch", "content", or "custom")

    The width of the chart element. This can be one of the following:
    
    "stretch" (default): The width of the element matches the width of the parent container.
    "content": The width of the element matches the width of its content, but doesn't exceed the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

custom width (int)
    
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.


## Feedback

Display a feedback widget. An icon-based button group available in three styles. Commonly used in chat and AI apps to allow users to rate responses.

Function signature
    st.feedback(options="thumbs", *, key=None, default=None, disabled=False, width="content")

options ("thumbs", "faces", or "stars")

    Default: "thumbs"
    In properties pane should be a selectbox with options "thumbs", "faces", and "stars".

    The feedback options displayed to the user:
    "thumbs" (default): A thumb-up and thumb-down button group.
    "faces": A row of five buttons with facial expressions depicting increasing satisfaction from left to right.
    "stars": A row of star icons, allowing the user to select a rating from one to five stars.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

default (int or None)

    Default: None
    Don't create in properties pane. Generate in code with default value None.

disabled (bool)

    Default: False
    In properties pane display as a checkbox with default value False.

width ("content", "stretch", or "custom")

    The width of the feedback widget. This can be one of the following:

    "content" (default): The width of the widget matches the width of its content, but doesn't exceed the width of the parent container.
    "stretch": The width of the widget matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

custom width (int)

    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The widget has a fixed width. If the specified width is greater than the width of the parent container, the width of the widget matches the width of the parent container.


## Pills

Display a horizontal row of clickable pill-shaped buttons for single or multi-selection.

Function signature
    st.pills(label, options, *, selection_mode="single", default=None, format_func=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="content", bind=None)

label (str)

    Default: "Pills"
    The label displayed above the pills widget.

options (Iterable)

    Default: ["Option 1", "Option 2", "Option 3"]
    In properties pane: comma-separated text field.
    Labels for the pill options. Each label will be cast to str internally.

selection_mode ("single" or "multi")

    Default: "single"
    In properties pane should be a selectbox with options "single" and "multi".

    "single" (default): Only one pill can be selected at a time. Returns a single value or None.
    "multi": Multiple pills can be selected. Returns a list of selected values.

default (str, list, or None)

    Default: None
    Don't create in properties pane. Generate in code with default value None.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

help (str or None)

    Default: None
    A tooltip that gets displayed when the widget is hovered over. If this is None (default), no tooltip is displayed.

disabled (bool)

    Default: False
    In properties pane display as a checkbox with default value False.

label_visibility ("visible", "hidden", or "collapsed")

    Default: "visible"
    In properties pane should be a selectbox with options "visible", "hidden", and "collapsed".

    "visible" (default): The label is displayed above the pills.
    "hidden": An empty spacer is shown instead of the label.
    "collapsed": No label or spacer is displayed.

icon (str or None)

    Default: None
    Should not be displayed in properties pane. Generate in code and set to None(None by default).

format_func, on_change, args, kwargs

    Should not be displayed in properties pane. Not generated in code.

width ("content", "stretch", or "custom")

    The width of the feedback widget. This can be one of the following:

    "content" (default): The width of the widget matches the width of its content, but doesn't exceed the width of the parent container.
    "stretch": The width of the widget matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

custom width (int)

    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The widget has a fixed width. If the specified width is greater than the width of the parent container, the width of the widget matches the width of the parent container.


## Segmented control

Display a segmented control widget. A linear set of segments where each option functions like a toggle button.

Function signature
    st.segmented_control(label, options, *, selection_mode="single", default=None, format_func=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="content", bind=None)

label (str)

    Default: "Segmented control"
    The label displayed above the segmented control widget.

options (Iterable)

    Default: ["Option 1", "Option 2", "Option 3"]
    In properties pane: comma-separated text field.
    Labels for the segments. Each label will be cast to str internally.

selection_mode ("single" or "multi")

    Default: "single"
    In properties pane should be a selectbox with options "single" and "multi".

    "single" (default): Only one segment can be selected at a time. Returns a single value or None.
    "multi": Multiple segments can be selected. Returns a list of selected values.

default (str, list, or None)

    Default: None
    Don't create in properties pane. Generate in code with default value None.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

help (str or None)

    Default: None
    A tooltip that gets displayed next to the widget label. If this is None (default), no tooltip is displayed.

disabled (bool)

    Default: False
    In properties pane display as a checkbox with default value False.

label_visibility ("visible", "hidden", or "collapsed")

    Default: "visible"
    In properties pane should be a selectbox with options "visible", "hidden", and "collapsed".

    "visible" (default): The label is displayed above the widget.
    "hidden": An empty spacer is shown instead of the label.
    "collapsed": No label or spacer is displayed.

format_func, on_change, args, kwargs

    Should not be displayed in properties pane. Not generated in code.

width ("content", "stretch", or "custom")

    The width of the segmented control widget. This can be one of the following:

    "content" (default): The width of the widget matches the width of its content, but doesn't exceed the width of the parent container.
    "stretch": The width of the widget matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

custom width (int)

    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The widget has a fixed width. If the specified width is greater than the width of the parent container, the width of the widget matches the width of the parent container.


## Select slider

Display a slider widget to select items from a list. Supports single value selection and range selection (two-value tuple).

Function signature
    st.select_slider(label, options=(), value=None, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible", width="stretch", bind=None)

label (str)

    Default: "Select slider"
    The label displayed above the slider widget.

options (Iterable)

    Default: "Option 1, Option 2, Option 3"
    In properties pane: comma-separated text field.
    Labels for the select options. Each label will be cast to str internally.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

value (a supported type or None)

    Default: None
    Don't create in properties pane. Generate in code with default value None (Streamlit defaults to the first option at runtime).

help (str or None)

    Default: None (empty string in pane)
    A tooltip that gets displayed next to the widget label. If this is None (default), no tooltip is displayed.

disabled (bool)

    Default: False
    In properties pane display as a checkbox with default value False.

label_visibility ("visible", "hidden", or "collapsed")

    Default: "visible"
    In properties pane should be a selectbox with options "visible", "hidden", and "collapsed".

    "visible" (default): The label is displayed above the slider.
    "hidden": An empty spacer is shown instead of the label.
    "collapsed": No label or spacer is displayed.

format_func, on_change, args, kwargs, bind

    Should not be displayed in properties pane. Not generated in code.

width ("stretch" or "custom")

    The width of the slider widget. This can be one of the following:

    "stretch" (default): The width of the widget matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

    Note: st.select_slider only supports "stretch" or an integer width — there is no "content" option.

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The widget has a fixed width. If the specified width is greater than the width of the parent container, the width of the widget matches the width of the parent container.


## Datetime input

Display a date and time input widget.

Function signature
    st.datetime_input(label, value="now", min_value=None, max_value=None, *, key=None, help=None, on_change=None, args=None, kwargs=None, format="YYYY/MM/DD", step=900, disabled=False, label_visibility="visible", width="stretch", bind=None)

label (str)

    Default: "Datetime input"
    The label displayed above the widget.

value (str)

    Default: "now"
    In properties pane: text field.
    Accepted values: "now", an ISO datetime string ("YYYY-MM-DD hh:mm"), or empty string for None.
    "now": The widget initializes with the current date and time.
    An ISO-formatted string: The widget initializes with the parsed value.
    Empty string: The widget initializes with no value and returns None until the user selects a datetime. Generate in code as None.

min_value (str or None)

    Default: "" (None)
    In properties pane: text field. Same accepted formats as value.
    If empty, generate in code as None (Streamlit defaults to ten years before the initial value).

max_value (str or None)

    Default: "" (None)
    In properties pane: text field. Same accepted formats as value.
    If empty, generate in code as None (Streamlit defaults to ten years after the initial value).

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

help (str or None)

    Default: None (empty string in pane)
    A tooltip that gets displayed next to the widget label. If this is None (default), no tooltip is displayed.

format (str)

    Default: "YYYY/MM/DD"
    In properties pane should be a selectbox with the following options:
    "YYYY/MM/DD", "DD/MM/YYYY", "MM/DD/YYYY",
    "YYYY-MM-DD", "DD-MM-YYYY", "MM-DD-YYYY",
    "YYYY.MM.DD", "DD.MM.YYYY", "MM.DD.YYYY"
    Controls how the date portion is displayed in the widget interface. Does not affect the time format.

step (int)

    Default: 900
    In properties pane: integer input field (seconds).
    The stepping interval in seconds. Must be between 60 and 82800 (23 hours).
    Common values: 60 (1 min), 300 (5 min), 900 (15 min), 1800 (30 min), 3600 (1 hour).

disabled (bool)

    Default: False
    In properties pane display as a checkbox with default value False.

label_visibility ("visible", "hidden", or "collapsed")

    Default: "visible"
    In properties pane should be a selectbox with options "visible", "hidden", and "collapsed".

    "visible" (default): The label is displayed above the widget.
    "hidden": An empty spacer is shown instead of the label.
    "collapsed": No label or spacer is displayed.

on_change, args, kwargs, bind

    Should not be displayed in properties pane. Not generated in code.

width ("stretch" or "custom")

    The width of the widget. This can be one of the following:

    "stretch" (default): The width of the widget matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

    Note: st.datetime_input only supports "stretch" or an integer width — there is no "content" option.

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The widget has a fixed width. If the specified width is greater than the width of the parent container, the widget matches the container width.


## Time input

Display a time input widget.

Function signature
    st.time_input(label, value="now", key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible", step=900, width="stretch", bind=None)

label (str)

    Default: "Time input"
    The label displayed above the widget.

value (str)

    Default: "now"
    In properties pane: text field.
    Accepted values: "now", an ISO time string ("hh:mm" or "hh:mm:ss"), or empty string for None.
    "now": The widget initializes with the current time.
    An ISO-formatted time string: The widget initializes with the given time.
    Empty string: The widget initializes with no time and returns None until the user selects a time. Generate in code as None.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

help (str or None)

    Default: None (empty string in pane)
    A tooltip that gets displayed next to the widget label. If this is None (default), no tooltip is displayed.

step (int)

    Default: 900
    In properties pane: integer input field (seconds).
    The stepping interval in seconds. Must be between 60 and 82800 (23 hours).
    Common values: 60 (1 min), 300 (5 min), 900 (15 min), 1800 (30 min), 3600 (1 hour).

disabled (bool)

    Default: False
    In properties pane display as a checkbox with default value False.

label_visibility ("visible", "hidden", or "collapsed")

    Default: "visible"
    In properties pane should be a selectbox with options "visible", "hidden", and "collapsed".

    "visible" (default): The label is displayed above the widget.
    "hidden": An empty spacer is shown instead of the label.
    "collapsed": No label or spacer is displayed.

on_change, args, kwargs, bind

    Should not be displayed in properties pane. Not generated in code.

width ("stretch" or "custom")

    The width of the time input widget. This can be one of the following:

    "stretch" (default): The width of the widget matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

    Note: st.time_input only supports "stretch" or an integer width — there is no "content" option.

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The widget has a fixed width. If the specified width is greater than the width of the parent container, the width of the widget matches the width of the parent container.




## Audio

Display an audio player.

Function signature
    st.audio(data, format="audio/wav", start_time=0, *, sample_rate=None, end_time=None, loop=False, autoplay=False, width="stretch")

data (str)

    Default: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    Don't create in properties pane. Generate in code with default value (a public sample audio URL). User can replace with their own URL or file path in the generated code.

format (str)

    Default: "audio/wav"
    In properties pane should be a selectbox with the following options:
    "audio/wav", "audio/mp3", "audio/ogg", "audio/mpeg", "audio/flac"
    The MIME type of the audio file.

start_time (int)

    Default: 0
    In properties pane: integer input field (seconds).
    The time in seconds from which the element should start playing. Must be 0 or a positive integer.

end_time (int or None)

    Default: None
    Don't create in properties pane. Generate in code as None (plays through to the end).

loop (bool)

    Default: False
    In properties pane display as a checkbox with default value False.
    Whether the audio should loop playback.

autoplay (bool)

    Default: False
    In properties pane display as a checkbox with default value False.
    Whether the audio file should start playing automatically. Note: browsers block autoplay if the user has not interacted with the page.

sample_rate

    Should not be displayed in properties pane. Not generated in code.
    Only required when data is a NumPy array, which is not supported in the designer.

width ("stretch" or "custom")

    The width of the audio player element. This can be one of the following:

    "stretch" (default): The width of the element matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

    Note: st.audio only supports "stretch" or an integer width — there is no "content" option.

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.


## Audio input

st.audio_input(label, *, sample_rate=16000, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

label (str)

    A short label explaining to the user what this widget is used for.
    In properties pane: text field.
    Default: "Record audio"
    Always generate in code as the first positional argument.

sample_rate (int or None)

    The target sample rate for the audio recording in Hz.
    In properties pane: selectbox with options:
      8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000, None
    Default: 16000
    Generate in code only if value != 16000.
    If "None" selected, generate as Python `None`.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

help (str or None)

    Default: None (empty string in pane)
    A tooltip displayed next to the widget label.
    Generate in code only if non-empty.

disabled (bool)

    Default: False
    In properties pane: checkbox.
    Generate in code only if True.

label_visibility ("visible", "hidden", or "collapsed")

    Default: "visible"
    In properties pane: selectbox with options "visible", "hidden", "collapsed".
    Generate in code only if value != "visible".

on_change, args, kwargs

    Not displayed in properties pane. Not generated in code.

width ("stretch" or "custom")

    The width of the audio input widget.
    In properties pane: selectbox with options "stretch" and "custom".
    Default: "stretch"
    - "stretch" (default): Width matches parent container.
    - "custom": Fixed width in pixels. Controlled by custom_width.
    Note: st.audio_input only supports "stretch" or an integer — there is no "content" option.
    Always generate in code.

custom_width (int)

    Default: 320
    Enabled only when width is "custom".
    An integer specifying the width in pixels.


## Camera input

st.camera_input(label, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible", width="stretch")

label (str)

    A short label explaining to the user what this widget is used for.
    In properties pane: text field.
    Default: "Take a picture"
    Always generate in code as the first positional argument.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.
    Always generate in code.

help (str or None)

    Default: None (empty string in pane)
    A tooltip displayed next to the widget label.
    Generate in code only if non-empty.

disabled (bool)

    Default: False
    In properties pane: checkbox.
    Generate in code only if True.

label_visibility ("visible", "hidden", or "collapsed")

    Default: "visible"
    In properties pane: selectbox with options "visible", "hidden", "collapsed".
    Generate in code only if value != "visible".

on_change, args, kwargs

    Not displayed in properties pane. Not generated in code.

width ("stretch" or "custom")

    The width of the camera input widget.
    In properties pane: selectbox with options "stretch" and "custom".
    Default: "stretch"
    - "stretch" (default): Width matches parent container.
    - "custom": Fixed width in pixels. Controlled by custom_width.
    Note: st.camera_input only supports "stretch" or an integer — there is no "content" option.
    Always generate in code.

custom_width (int)

    Default: 320
    Enabled only when width is "custom".
    An integer specifying the width in pixels.


## Sidebar

st.sidebar

This is a **container widget** — follow `.github/instructions/container-widget.instructions.md`.

The sidebar is a special built-in container pinned to the left of the app. Any element can be placed inside it using `with st.sidebar:` notation.

label (str)

    Internal label for the sidebar (displayed in hierarchy/canvas).
    In properties pane: text field.
    Default: "Sidebar"
    Not passed to `st.sidebar`. Used only for UI display (comment above the sidebar block in generated code).

No other configurable properties. The sidebar has no parameters in its function signature.

Codegen:
    Generate: `with st.sidebar:`
    Add a `# Sidebar` comment above the block.
    Children are indented inside the block.
    If no children, generate `pass`.

on_change, args, kwargs, key

    Not applicable. Not displayed in properties pane. Not generated in code.


## Tabs

st.tabs(tabs, *, width="stretch", default=None, key=None, on_change="ignore", args=None, kwargs=None)

This is a **container widget** that inserts multiple child containers as tabs.

Recommended model structure:
- Parent widget type: `tabs`
- Auto-managed child container widget type: `tab`
- Child widgets added inside a specific `tab` container

Parent properties

label (str)

    Internal label for the tabs container (displayed in hierarchy/canvas).
    In properties pane: text field.
    Default: "Tabs"
    Not passed to `st.tabs`. Used only for UI display and optional generated code comment.

tabs (int)

    The number of tab containers to create.
    In properties pane: integer input with minimum 1.
    Default: 2
    Changing this value should auto-sync child `tab` containers, similar to `columns_container`.
    If the count is reduced, remove deleted tab subtrees.

width ("stretch" or "custom")

    The width of the tabs container.
    In properties pane: selectbox with options "stretch" and "custom".
    Default: "stretch"
    - "stretch" (default): Width matches the parent container.
    - "custom": Fixed width in pixels. Controlled by `custom_width`.
    Note: `st.tabs` only supports "stretch" or an integer width.

custom_width (int)

    Default: 320
    Enabled only when width is "custom".
    An integer specifying the width in pixels.

default (str or None)

    The default selected tab label.
    In properties pane: selectbox or text field populated from child tab labels, with an empty option for None.
    Default: None
    If None, the first tab is selected.
    If set, the value must match one of the current child `tab.label` values.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.
    Especially useful when `on_change` is not "ignore".

on_change ("ignore" or "rerun")

    In properties pane: selectbox with options "ignore" and "rerun".
    Default: "ignore"
    - "ignore" (default): Tabs don't track selected state.
    - "rerun": Tabs track selected state and rerun the app when selection changes.
    Do not support callable callbacks in the designer.

args, kwargs

    Not displayed in properties pane. Not generated in code.

Child `tab` properties

label (str)

    The visible tab label.
    In properties pane: text field.
    Default: "Tab 1", "Tab 2", ...
    This value is used in the list passed to `st.tabs([...])`.
    Supports the same label text/Markdown behavior as Streamlit tab labels.

Codegen:
    Generate a single `st.tabs([...])` call from the ordered child `tab.label` values.
    Assign the returned tab containers to local variables.
    Emit one `with <tab_var>:` block per child tab.
    Render each tab's children inside its block.
    If a tab has no children, generate `pass` inside that block.

Preview:
    Show tabs as a local preview-only tab strip inside the preview pane.
    Render child widgets under the selected tab.
    If a tab is empty, display a placeholder hint like "Add child widgets here".


## Chat input

Display a chat input widget. When used in the main body of an app, it is pinned to the bottom of the page. When nested inside a layout container (sidebar, columns, tabs, etc.), it renders inline.

Function signature
    st.chat_input(placeholder="Your message", *, key=None, max_chars=None, accept_file=False, accept_audio=False, disabled=False, on_submit=None, args=None, kwargs=None, width="stretch")

    Note: The user-provided signature includes `height="content"`, but the installed
    Streamlit runtime does not support `height` for `st.chat_input`. The `height`
    property is documented below for future reference but is NOT displayed in the
    properties pane and NOT generated in code until the runtime is updated.

placeholder (str)

    Default: "Your message"
    A placeholder text shown when the chat input is empty.

key (str, int, or None)

    Auto-generated from widget id. Display generated key in properties pane; if key is changed, apply the change to generated code as well.

disabled (bool)

    Default: False
    In properties pane display as a checkbox with default value False.

max_chars (int or None)

    Default: None
    Don't create in properties pane. Generate in code with default value None (no limit).

accept_file (bool, "multiple", or "directory")

    Default: False
    Don't create in properties pane. Generate in code with default value False.

accept_audio (bool)

    Default: False
    Don't create in properties pane. Generate in code with default value False.

max_upload_size, file_type, audio_sample_rate, on_submit, args, kwargs

    Should not be displayed in properties pane. Not generated in code.

width ("stretch" or "custom")

    The width of the chat input widget. This can be one of the following:

    "stretch" (default): The width of the widget matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

    Note: st.chat_input only supports "stretch" or an integer width — there is no "content" option.

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The widget has a fixed width. If the specified width is greater than the width of the parent container, the width of the widget matches the width of the parent container.

height ("content", "stretch", or "custom")

    NOT implemented in the current project runtime. The installed Streamlit version
    does not support `height` for `st.chat_input`. Not displayed in properties pane.
    Not generated in code.

    When the runtime is updated, this can be:
    "content" (default): The widget uses the default single-line height and automatically expands based on input text.
    "stretch": The height stretches to fill the available height of the parent container. The parent container must have a defined height.
    "custom": The height is specified by the custom height property.

custom height (int)

    NOT implemented in the current project runtime.
    Default: 68
    if height property is not set to "custom" - disabled, else enabled.
    An integer specifying the minimum height in pixels. The widget still auto-expands based on text content. The minimum recommended height is 68 pixels (single line of text).


## Status

Display a status container to hold output from long-running tasks. Similar to st.expander but with an icon that reflects the task state.

This is a **container widget** — follow `.github/instructions/container-widget.instructions.md`.

Function signature
    st.status(label, *, expanded=False, state="running", width="stretch")

label (str)

    Default: "Status"
    The label of the status container.
    In properties pane: text field.
    Always generate in code as the first positional argument.

expanded (bool)

    Default: False
    Whether the status container initializes expanded.
    In properties pane: checkbox.
    Generate in code only if True.

state ("running", "complete", or "error")

    Default: "running"
    The initial state of the status container, which determines the icon shown:
    - "running" (default): A spinner icon.
    - "complete": A checkmark icon.
    - "error": An error icon.
    In properties pane: selectbox with options "running", "complete", "error".
    Generate in code only if value != "running".

width ("stretch" or "custom")

    The width of the status container. This can be one of the following:

    "stretch" (default): The width of the container matches the width of the parent container.
    "custom": The width of the container is specified by the custom width property.

    Note: st.status only supports "stretch" or an integer width ��� there is no "content" option.

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The container has a fixed width. If the specified width is greater than the width of the parent container, the width of the container matches the width of the parent container.

on_change, args, kwargs, key

    Not applicable. Not displayed in properties pane. Not generated in code.

Codegen:
    Generate: `with st.status("label", expanded=..., state=..., width=...):`
    Add a `# Status` comment above the block.
    Children are indented inside the block.
    If no children, generate `pass`.


## Progress

Display a progress bar.

Function signature
    st.progress(value, text=None, width="stretch")

value (int)

    Default: 50
    In properties pane: integer input field.
    The current progress value. Range: 0 to 100 inclusive.
    Generate in code as the first positional argument.

text (str or None)

    Default: "" (None)
    In properties pane: text field.
    A message to display above the progress bar. Supports GitHub-flavored Markdown (Bold, Italics, Strikethroughs, Inline Code, Links, Images).
    If empty string, generate in code as None.
    If non-empty, generate in code as the string value.

width ("stretch" or "custom")

    The width of the progress element. This can be one of the following:

    "stretch" (default): The width of the element matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

    Note: st.progress only supports "stretch" or an integer width — there is no "content" option.

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.


## Spinner

Display a loading spinner while executing a block of code.

Function signature
    st.spinner(text="In progress...", *, show_time=False, width="content")

text (str)

    Default: "In progress..."
    The text displayed next to the spinner.
    In properties pane: text field.
    Always generate in code as the first positional argument.
    The text can optionally contain GitHub-flavored Markdown of the following types: Bold, Italics, Strikethroughs, Inline Code, Links, and Images.

show_time (bool)

    Default: False
    Whether to show the elapsed time next to the spinner text.
    In properties pane: checkbox with default value False.
    Generate in code only if True.

width ("content", "stretch", or "custom")

    The width of the spinner element. This can be one of the following:

    "content" (default): The width of the element matches the width of its content, but doesn't exceed the width of the parent container.
    "stretch": The width of the element matches the width of the parent container.
    "custom": The width of the element is specified by the custom width property.

    In properties pane: selectbox with options "content", "stretch", "custom".

custom width (int)

    Default: 320
    if width property is not set to "custom" - disabled, else enabled.
    An integer specifying the width in pixels: The element has a fixed width. If the specified width is greater than the width of the parent container, the width of the element matches the width of the parent container.

on_change, args, kwargs, key

    Not applicable. Not displayed in properties pane. Not generated in code.

Codegen:
    Generate: `with st.spinner("text", show_time=..., width=...):`
    Add a `# Spinner` comment above the block.
    Children are indented inside the block.
    If no children, generate `pass`.
    `show_time` is only emitted when True.
    `width` is only emitted when not "content" (default).

