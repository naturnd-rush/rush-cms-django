from __future__ import annotations

import math
import re
from json import loads
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from rush.models.geometry import Geometry
    from rush.models.style.styles_on_layer import StylesOnLayer


def _coerce_numbers_deep(obj):
    """Convert string values that look like numbers to floats, mirroring coerceNumbersDeep in layer_preview.ts."""
    if isinstance(obj, dict):
        return {k: _coerce_numbers_deep(v) for k, v in obj.items()}
    if isinstance(obj, str):
        try:
            return float(obj)
        except ValueError:
            return obj
    return obj


def _evaluate_feature_mapping(feature_mapping: str, properties: dict) -> bool:
    """
    Evaluate a feature_mapping expression against feature properties.
    Mirrors the expr-eval Parser usage in layer_preview.ts getAppliedStyles().
    """
    expr = feature_mapping.strip()
    if expr == "true":
        return True
    if expr == "false":
        return False
    try:
        coerced = _coerce_numbers_deep(properties)
        result = eval(expr, {"__builtins__": {}, "true": True, "false": False}, coerced)  # noqa: S307
        return result is True
    except Exception:
        return False


def _blend_hex_colors(color1: str, color2: str, weight: float = 0.5) -> str:
    """Blend two hex colors. Mirrors blendHexColors in layer_preview.ts."""

    def to_rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    r1, g1, b1 = to_rgb(color1)
    r2, g2, b2 = to_rgb(color2)
    r = round(r1 * (1 - weight) + r2 * weight)
    g = round(g1 * (1 - weight) + g2 * weight)
    b = round(b1 * (1 - weight) + b2 * weight)
    return f"#{r:02X}{g:02X}{b:02X}"


def _interpolate_numbers(a, b):
    """Average two numbers. Mirrors interpolateNumbers in layer_preview.ts."""
    if a is None:
        return float(b) if b is not None else None
    if b is None:
        return float(a)
    return (float(a) + float(b)) / 2


def _get_default_polygon_style() -> dict:
    """Mirrors getDefaultPolygonStyle() in layer_preview.ts."""
    return {
        "fill": True,
        "fillColor": "#4B3EFF",
        "fillOpacity": 0.3,
        "stroke": True,
        "weight": 1,
        "opacity": 1,
        "color": "#4B3EFF",
        "dashArray": "1 10",
        "dashOffset": "0",
        "lineCap": "round",
        "lineJoin": "round",
    }


def _get_polygon_style(applied_styles: list[StylesOnLayer]) -> dict:
    """
    Build Leaflet PathOptions from a list of applied StylesOnLayer objects.
    Mirrors the style-merging logic in getPolygonStyleFunc() in layer_preview.ts.
    """
    draw_fill = False
    fill_opacity = None
    fill_color = None
    draw_stroke = False
    stroke_opacity = None
    stroke_color = None
    stroke_weight = None
    stroke_dash_array = ""
    stroke_dash_offset = None
    stroke_line_cap = "round"
    stroke_line_join = "round"

    for sol in applied_styles:
        style = sol.style
        if style.draw_fill:
            draw_fill = True
        if style.draw_stroke:
            draw_stroke = True

        fill_opacity = _interpolate_numbers(fill_opacity, style.fill_opacity)
        stroke_opacity = _interpolate_numbers(stroke_opacity, style.stroke_opacity)
        stroke_weight = _interpolate_numbers(stroke_weight, style.stroke_weight)

        if fill_color is None:
            fill_color = style.fill_color
        else:
            fill_color = _blend_hex_colors(fill_color, style.fill_color, 0.5)

        if stroke_color is None:
            stroke_color = style.stroke_color
        else:
            stroke_color = _blend_hex_colors(stroke_color, style.stroke_color, 0.5)

        if style.stroke_dash_array is not None:
            stroke_dash_array = style.stroke_dash_array
        if style.stroke_dash_offset is not None:
            stroke_dash_offset = style.stroke_dash_offset
        stroke_line_join = style.stroke_line_join
        stroke_line_cap = style.stroke_line_cap

    return {
        "fill": draw_fill,
        "fillColor": fill_color,
        "fillOpacity": fill_opacity,
        "stroke": draw_stroke,
        "weight": stroke_weight,
        "opacity": stroke_opacity,
        "color": stroke_color,
        "dashArray": stroke_dash_array,
        "dashOffset": stroke_dash_offset,
        "lineCap": stroke_line_cap,
        "lineJoin": stroke_line_join,
    }


def _get_marker_div_icon_props(base_media_url: str, style) -> dict:
    """
    Build Leaflet DivIcon properties for a marker.
    Mirrors getMarkerDivIconProps() in layer_preview.ts.
    """
    marker_image_width = float(style.marker_size)
    marker_radius = math.sqrt((marker_image_width / 2) ** 2 + (marker_image_width / 2) ** 2)
    html = (
        f"<div>"
        f'<div style="'
        f"width: {marker_radius * 2}px;"
        f"height: {marker_radius * 2}px;"
        f"background-color: {style.marker_background_color};"
        f"opacity: {style.marker_background_opacity};"
        f"border-radius: 50%;"
        f"display: flex;"
        f"position: absolute;"
        f'"></div>'
        f'<img src="{base_media_url}{style.marker_icon}"'
        f' style="'
        f"width: {marker_image_width}px;"
        f"height: {marker_image_width}px;"
        f"opacity: {style.marker_icon_opacity};"
        f"position: relative;"
        f"top: {marker_radius - (marker_image_width / 2)}px;"
        f"left: {marker_radius - (marker_image_width / 2)}px;"
        f'"/>'
        f"</div>"
    )
    return {
        "html": html,
        "className": "",
        "iconSize": [marker_radius * 2, marker_radius * 2],
        "iconAnchor": [marker_radius, marker_radius],
    }


def _get_circle_options(style) -> dict:
    """Build Leaflet CircleMarkerOptions from a Style. Mirrors getPointStyleFunc() circle branch."""
    return {
        "radius": float(style.circle_radius),
        "fill": True,
        "fillColor": style.circle_fill_color,
        "fillOpacity": float(style.circle_fill_opacity),
        "stroke": True,
        "color": style.circle_stroke_color,
        "weight": float(style.circle_stroke_weight),
        "opacity": float(style.circle_stroke_opacity),
        "lineCap": style.circle_stroke_line_cap,
        "lineJoin": style.circle_stroke_line_join,
        "dashArray": style.circle_stroke_dash_array,
        "dashOffset": style.circle_stroke_dash_offset,
    }


def _render_mustache(template: str, properties: dict) -> str:
    """
    Render a Mustache template string against properties.
    Handles the basic {{variable}} case used in popup/tooltip templates.
    """

    def replace(match):
        key = match.group(1).strip()
        return str(properties.get(key, ""))

    return re.sub(r"\{\{([^}]+)\}\}", replace, template)


def _get_popup_metadata(applied_styles: list[StylesOnLayer], properties: dict) -> dict:
    """
    Build popup metadata for a feature. Mirrors getPopupMetadata() and getPopupTemplate() in layer_preview.ts.
    draw_popup is inferred as True when a non-empty popup template exists on the StylesOnLayer.
    """
    popup_template = None
    for sol in applied_styles:
        if sol.popup:
            popup_template = sol.popup

    if not popup_template:
        return {"__hasPopup": False, "__popupHTML": None, "__popupOptions": None}

    popup_template = re.sub(
        r"<img(.*?)>",
        lambda m: m.group(0).replace("<img", '<img style="max-width:250px; height:auto;"'),
        popup_template,
    )
    has_image = bool(re.search(r"<img", popup_template))
    rendered = _render_mustache(popup_template, properties)
    return {
        "__hasPopup": True,
        "__popupHTML": rendered,
        "__popupOptions": {"maxWidth": 250, "minWidth": 250 if has_image else 0},
    }


def serialize_layer(
    geometries: QuerySet[Geometry],
    styles_on_layer: QuerySet[StylesOnLayer],
    base_media_url: str = "",
) -> dict:
    """
    Serialize a queryset of Geometry objects into the same JSON structure produced by
    serializeLayer() in layer_preview.ts — {"featureCollection": GeoJSON FeatureCollection}
    with Leaflet style properties injected into each feature's properties dict.

    For best performance, prefetch related objects on the querysets:
        geometries.select_related() if needed
        styles_on_layer.select_related("style").prefetch_related("tooltip")
    """
    sol_list = list(styles_on_layer)
    any_marker_styles = any(sol.style.draw_marker for sol in sol_list)

    features = []
    centroid_features = []

    for geometry in geometries:
        geom_dict = loads(geometry.data.geojson)
        properties = dict(geometry.properties)
        geom_type = geom_dict.get("type", "")
        is_point = geom_type in ("Point", "MultiPoint")

        applied = [sol for sol in sol_list if _evaluate_feature_mapping(sol.feature_mapping, properties)]

        if not is_point:
            style_props = _get_polygon_style(applied) if applied else _get_default_polygon_style()
            properties["__style"] = style_props
        else:
            marker_style = next((sol.style for sol in applied if sol.style.draw_marker), None)
            circle_style = next((sol.style for sol in applied if sol.style.draw_circle), None)
            if circle_style is not None:
                properties["__circleOptions"] = _get_circle_options(circle_style)
            elif marker_style is not None:
                properties["__pointDivIconStyleProps"] = _get_marker_div_icon_props(base_media_url, marker_style)

        popup_metadata = _get_popup_metadata(applied, properties)
        if popup_metadata["__hasPopup"]:
            properties.update(popup_metadata)

        centroid = geometry.data.centroid
        feature_center_lng = centroid.x
        feature_center_lat = centroid.y

        tooltip = None
        for sol in applied:
            try:
                tooltip = sol.tooltip
                break
            except Exception:
                continue

        if tooltip is not None:
            rendered_label = _render_mustache(tooltip.label, properties)
            properties["__hasTooltip"] = True
            properties["__tooltipLat"] = feature_center_lat
            properties["__tooltipLng"] = feature_center_lng
            properties["__tooltipHTML"] = rendered_label
            properties["__tooltipOptions"] = {
                "offset": [float(tooltip.offset_x), float(tooltip.offset_y)],
                "opacity": float(tooltip.opacity),
                "direction": tooltip.direction,
                "permanent": tooltip.permanent,
                "sticky": tooltip.sticky,
                "className": "leaflet-label",
            }
        else:
            properties["__hasTooltip"] = False

        if geom_type in ("Polygon", "MultiPolygon") and any_marker_styles:
            marker_applied = [sol for sol in applied if sol.style.draw_marker]
            if marker_applied:
                centroid_props = {
                    **_get_marker_div_icon_props(base_media_url, marker_applied[0].style),
                    **popup_metadata,
                }
                centroid_features.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [feature_center_lng, feature_center_lat]},
                        "properties": centroid_props,
                    }
                )

        features.append(
            {
                "type": "Feature",
                "geometry": geom_dict,
                "properties": properties,
            }
        )

    return {
        "featureCollection": {
            "type": "FeatureCollection",
            "features": centroid_features + features,
        }
    }
