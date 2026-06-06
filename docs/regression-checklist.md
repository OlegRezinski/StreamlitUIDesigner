# Regression Checklist

Use this checklist before marking a milestone complete.

## Codegen
- Generated code runs without manual edits.
- Widget order in code matches canvas order.
- Keys are stable and unique.
- No unsafe constructs (no exec/eval in generated code).
- Metric widget emits `st.metric(...)` with configured props.
- Json widget emits `st.json(...)` with expected expanded/width behavior.
- Area chart widget emits `st.area_chart(...)` using sample chart data and configured props.
- Bar chart widget emits `st.bar_chart(...)` using sample chart data and configured props.
- Line chart widget emits `st.line_chart(...)` using sample chart data and configured props.
- Line chart generated code includes `import pandas as pd`, `# Replace with your data` comment, and inline DataFrame literal.
- Scatter chart widget emits `st.scatter_chart(...)` using inline scatter data and configured props.
- Scatter chart generated code includes `import pandas as pd`, `# Replace with your data` comment, and inline DataFrame literal.
- Graphviz chart widget emits `st.graphviz_chart(...)` using sample DOT graph data and configured props.
- Graphviz chart generated code includes `# Replace with your data` comment and inline DOT graph string.
- Download button widget emits `st.download_button(...)` with configured label, data, file_name, type, icon, and disabled props.
- Link button widget emits `st.link_button(...)` with configured label, url, type, icon, and disabled props.
- Page link widget emits `st.page_link(...)` with configured page, label, icon, disabled, and width props.
- Feedback widget emits `st.feedback(...)` with configured options, key, default, disabled, and width props.
- Pills widget emits `st.pills(...)` with configured label, options, selection_mode, key, default, disabled, and label_visibility props.
- Segmented control widget emits `st.segmented_control(...)` with configured label, options, selection_mode, key, default, disabled, label_visibility, and width props.
- Select slider widget emits `st.select_slider(...)` with configured label, options, value, key, disabled, label_visibility, and width props.
- Datetime input widget emits `st.datetime_input(...)` with configured label, value, min_value, max_value, key, format, step, disabled, label_visibility, and width props.
- Time input widget emits `st.time_input(...)` with configured label, value, key, step, disabled, label_visibility, and width props.
- Chat input widget emits `st.chat_input(...)` with configured placeholder, key, max_chars, accept_file, accept_audio, disabled, and width props.
- Audio widget emits `st.audio(...)` with configured format, start_time, end_time, loop, autoplay, and width props.
- Image widget emits `st.image(...)` with configured image URL, caption, width, output_format, and link props.
- Logo widget emits `st.logo(...)` with configured image, size, and icon_image props.
- PDF widget emits `st.pdf(...)` with configured height (custom int or 'stretch') and key props; includes `# Replace with your data` comment.
- Video widget emits `st.video(...)` with configured url, start_time, loop, autoplay, muted, and width props.
- Video generated code includes `# Replace with your video data` comment.


## Preview
- Preview renders all widgets in order.
- Preview reflects latest property edits.
- No Streamlit key collisions in preview.
- Metric widget preview updates for value/delta, chart type/data, and size modes.
- Json widget preview renders sample JSON data and responds to expanded/width modes.
- Area chart preview renders sample chart data and reflects configured axes/size options.
- Bar chart preview renders sample chart data and reflects horizontal/sort/stack and size options.
- Line chart preview renders sample chart data and reflects configured axes/size options.
- Scatter chart preview renders locally generated scatter data and reflects configured size/axes/dimension options.
- Graphviz chart preview renders sample DOT graph and reflects configured dimension options.
- Download button preview renders `st.download_button` with configured properties and width styling.
- Link button preview renders `st.link_button` with configured properties and width styling.
- Page link preview renders `st.page_link` with configured properties and width styling.
- Feedback preview renders `st.feedback` with configured options, disabled, and width styling.
- Pills preview renders `st.pills` with configured label, options, selection_mode, disabled, and label_visibility.
- Segmented control preview renders `st.segmented_control` with configured label, options, selection_mode, disabled, label_visibility, and width.
- Select slider preview renders `st.select_slider` with configured label, options, disabled, label_visibility, and width.
- Datetime input preview renders `st.datetime_input` with configured label, value, format, step, disabled, label_visibility, and width.
- Time input preview renders `st.time_input` with configured label, value, step, disabled, label_visibility, and width.
- Chat input preview renders `st.chat_input` with configured placeholder, disabled, and width.
- Audio preview renders `st.audio` with configured format, start_time, loop, autoplay, and width.
- Image preview renders `st.image` with configured URL, caption, width, and output_format.
- Logo preview renders `st.logo` with configured image, size, and icon_image.
- PDF preview renders `st.pdf` with configured height (custom/stretch) and key.
- Video preview renders `st.video` with configured url, start_time, loop, autoplay, muted, and width.

## Designer UI
- Add/select/reorder/remove works without crashes.
- Properties panel updates immediately.
- Selected widget highlight stays consistent after reorder.

## Validation
- Invalid date inputs show a warning and do not crash.
- Slider/number values are clamped to min/max.
- Multiselect defaults outside options are ignored.

## Video
- [ ] Video widget appears in palette under Media.
- [ ] Adding video shows a player in the canvas.
- [ ] Changing data URL updates the player.
- [ ] loop/autoplay/muted toggles reflect in generated code only when True.
- [ ] start_time generates only when non-zero.
- [ ] width="stretch" generates `width='stretch'`; width="custom" generates integer.
- [ ] Generated code contains `# Replace with your video data` comment.

## PDF
- [ ] PDF widget appears in palette under Media.
- [ ] Adding PDF shows a placeholder in the canvas.
- [ ] height="stretch" generates `height='stretch'`.
- [ ] height="custom" generates integer height from custom_height.
- [ ] Invalid custom_height defaults to 500.
- [ ] Generated code contains `# Replace with your data` comment.
## Container (updated)
- [ ] Container appears in palette under "Layouts and containers".
- [ ] Adding container shows a bordered preview with "?? st.container � <label>" caption.
- [ ] Children added inside it are visible in the preview.
- [ ] Selecting the container in hierarchy sets the Container pane to it.
- [ ] Selecting a child in hierarchy sets the Container pane to the parent container.
- [ ] Moving the container with ??/?? moves the entire block (widget + children).
- [ ] Generated code uses `with st.container(width=..., height=..., ...):`.
- [ ] border="None" generates no border= argument.
- [ ] border="True"/"False" generates border=True/False correctly.
- [ ] width="custom" generates integer, "stretch"/"content" generate quoted strings.
- [ ] height="custom" generates integer, others generate quoted strings.
- [ ] horizontal=False is omitted; horizontal=True generates horizontal=True.
- [ ] horizontal_alignment="left" omitted; others generated.
- [ ] vertical_alignment="top" omitted; others generated.
- [ ] gap="small" omitted; others generated; "None" generates gap=None.
- [ ] background_color="#FFFFFF" generates no CSS; any other color injects <style>.
- [ ] Empty container generates `pass` placeholder.
## Form
- [ ] Widget appears in palette under "Layouts and containers".
- [ ] Adding widget shows a bordered preview placeholder with a disabled Submit button.
- [ ] Children added inside it are visible in the preview.
- [ ] Selecting the widget in hierarchy sets the Container pane to it.
- [ ] Selecting a child in hierarchy sets the Container pane to the parent form.
- [ ] Moving the widget with ??/?? moves the entire block (widget + children).
- [ ] A neighbouring widget moving past it swaps with the whole block.
- [ ] Generated code contains `with st.form(key):` with children indented.
- [ ] Generated code always ends the form body with `st.form_submit_button('Submit')`.
- [ ] Empty block generates only `st.form_submit_button('Submit')` (no `pass`).
- [ ] key is auto-generated as `form_{widget.id[:8]}` if left blank.
## Popover
- [ ] Widget appears in palette under "Layouts and containers".
- [ ] Adding widget shows a bordered preview placeholder in the canvas.
- [ ] Children added inside it are visible in the preview.
- [ ] Selecting the widget in hierarchy sets the Container pane to it.
- [ ] Selecting a child in hierarchy sets the Container pane to the parent popover.
- [ ] Moving the widget with up/down moves the entire block (widget + children).
- [ ] A neighbouring widget moving past it swaps with the whole block.
- [ ] Generated code contains `with st.popover(label):` with children indented.
- [ ] Empty block generates `pass` placeholder.
- [ ] type="secondary" is not emitted; other types are emitted.
- [ ] on_change="rerun" emits `on_change=st.rerun` and key in generated code.

## Audio input

- [ ] Widget appears in palette under the correct category.
- [ ] Adding widget shows a mic/audio input in the preview pane.
- [ ] Generated code contains `st.audio_input(label, key=..., width=...)`.
- [ ] Default sample_rate (16000) is not emitted in generated code.
- [ ] Non-default sample_rate values are emitted.
- [ ] sample_rate=None is emitted as Python None.
- [ ] help, disabled, label_visibility are emitted only when non-default.
- [ ] Custom width generates integer width in code.

## Camera input

- [ ] Widget appears in palette under the correct category.
- [ ] Adding widget shows a camera input widget in the preview pane.
- [ ] Generated code contains `img_file_buffer = st.camera_input(label, key=..., width=...)`.
- [ ] key is always emitted (auto-generated if blank).
- [ ] help, disabled, label_visibility are emitted only when non-default.
- [ ] Custom width generates integer width in code.
- [ ] Stretch width generates `width='stretch'` in code.

## Sidebar

- [ ] Widget appears in palette under "Layouts and containers".
- [ ] Adding widget shows a bordered preview placeholder in the canvas.
- [ ] Children added inside it are visible in the preview.
- [ ] Selecting the widget in hierarchy sets the Container pane to it.
- [ ] Selecting a child in hierarchy sets the Container pane to the parent sidebar.
- [ ] Moving the widget with ⬆️/⬇️ moves the entire block (widget + children).
- [ ] A neighbouring widget moving past it swaps with the whole block.
- [ ] Generated code contains `with st.sidebar:` (no parentheses) with children indented.
- [ ] Empty block generates `pass` placeholder.
- [ ] Only one sidebar can exist per design.


## Tabs

- [ ] 	abs widget appears in palette under 'Layouts and containers'
- [ ] 	ab widget is NOT shown in palette
- [ ] Adding 	abs auto-creates 2 child 	ab widgets
- [ ] Container selector shows 	abs widget as an option
- [ ] When 	abs is selected as container, a 'Target tab' selector appears
- [ ] Adding widget to a 	abs container routes it under the correct 	ab
- [ ] Preview renders st.tabs([...]) with correct labels
- [ ] Empty tab previews show placeholder text
- [ ] Children of tabs render inside correct tab container
- [ ] Codegen emits 	abs_1 = st.tabs([...], width=...)
- [ ] Codegen emits with tabs_1[i]: blocks
- [ ] Empty tabs emit pass
- [ ] width='custom' emits integer value in codegen
- [ ] Valid default label is emitted in codegen
- [ ] Invalid default label is NOT emitted in codegen

## Chat input
- [ ] Widget appears in palette under "Input elements".
- [ ] Adding widget creates instance with correct default props.
- [ ] Generated code contains `st.chat_input(...)` with placeholder, key, max_chars=None, accept_file=False, accept_audio=False, width.
- [ ] Custom key prop overrides auto-generated key in codegen.
- [ ] width="custom" with custom_width generates integer width in codegen.
- [ ] disabled=True generates disabled=True in code.
- [ ] Preview renders the widget inline.

## Status

- [ ] Widget appears in palette under "Chat elements".
- [ ] Adding widget shows a status preview in the canvas.
- [ ] Children added inside it are visible in the preview.
- [ ] Selecting the widget in hierarchy sets the Container pane to it.
- [ ] Selecting a child in hierarchy sets the Container pane to the parent status.
- [ ] Moving the widget with ⬆️/⬇️ moves the entire block (widget + children).
- [ ] A neighbouring widget moving past it swaps with the whole block.
- [ ] Generated code contains `with st.status():` with children indented.
- [ ] Empty block generates `pass` placeholder.
- [ ] `expanded=True` prop emits `expanded=True` in codegen.
- [ ] `state` prop emits `state=` only when not "running".
- [ ] `width="custom"` with `custom_width` generates integer width in codegen.

## Progress

- [ ] Widget appears in palette under "Other".
- [ ] Adding widget shows a progress bar in the canvas.
- [ ] Changing value (0-100) updates the progress bar in preview.
- [ ] Values outside 0-100 are clamped in codegen and preview.
- [ ] Empty text generates `text=None` in code.
- [ ] Non-empty text generates `text='...'` in code.
- [ ] width="stretch" generates `width='stretch'` in codegen.
- [ ] width="custom" with custom_width generates integer width in codegen.
- [ ] Generated code contains `st.progress(value, text=..., width=...)`.

## Spinner

- [ ] Widget appears in palette under "Other".
- [ ] Adding widget shows a bordered preview placeholder in the canvas.
- [ ] Children added inside it are visible in the preview.
- [ ] Selecting the widget in hierarchy sets the Container pane to it.
- [ ] Selecting a child in hierarchy sets the Container pane to the parent spinner.
- [ ] Moving the widget with up/down moves the entire block (widget + children).
- [ ] A neighbouring widget moving past it swaps with the whole block.
- [ ] Generated code contains `with st.spinner('text'):` with children indented.
- [ ] Empty block generates `pass` placeholder.
- [ ] `show_time=True` emits `show_time=True` in codegen; False is not emitted.
- [ ] `width="content"` (default) is not emitted in codegen.
- [ ] `width="stretch"` emits `width='stretch'` in codegen.
- [ ] `width="custom"` with `custom_width` generates integer width in codegen.

## Button (updated)

- [ ] Widget appears in palette under "Input elements".
- [ ] Adding widget shows a native st.button in the canvas.
- [ ] Generated code uses `st.button(label, key=..., type=..., width=...)`.
- [ ] No CSS/unsafe_allow_html in generated code.
- [ ] help is only emitted when non-empty.
- [ ] icon is only emitted when non-empty.
- [ ] disabled is only emitted when True.
- [ ] width="content" generates `width='content'`.
- [ ] width="stretch" generates `width='stretch'`.
- [ ] width="custom" with custom_width generates integer width.
- [ ] Custom key overrides auto-generated key.
- [ ] type="primary"/"secondary"/"tertiary" generates correctly.
