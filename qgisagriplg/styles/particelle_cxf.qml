<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.16.7-Hannover" labelsEnabled="1" styleCategories="Symbology|Labeling">
  <renderer-v2 symbollevels="0" forceraster="0" type="RuleRenderer" enableorderby="0">
    <rules key="{846088b7-d0ec-4079-809d-0e076a0fa8a2}">
      <rule symbol="0" key="{70a6178c-634f-4b76-818a-17207a785803}" filter=" &quot;particella&quot; like 'ID%'" label="Acque"/>
      <rule symbol="1" key="{4b31fbf2-237b-42fa-8cc2-1d85b781d41a}" filter=" &quot;particella&quot; like 'ST%'" label="Strade"/>
      <rule symbol="2" key="{33b4859a-2ab2-4147-8a56-5942cd7500f8}" filter="ELSE" label="Particelle"/>
    </rules>
    <symbols>
      <symbol name="0" alpha="0.5" type="fill" force_rhr="0" clip_to_extent="1">
        <layer class="SimpleFill" locked="0" enabled="1" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="73,236,250,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="22,22,166,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.46" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="1" alpha="0.5" type="fill" force_rhr="0" clip_to_extent="1">
        <layer class="SimpleFill" locked="0" enabled="1" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="155,146,153,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="22,22,166,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.46" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="2" alpha="0.5" type="fill" force_rhr="0" clip_to_extent="1">
        <layer class="SimpleFill" locked="0" enabled="1" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="138,243,145,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="22,22,166,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.46" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style multilineHeight="1" fontLetterSpacing="0" fontWordSpacing="0" fontUnderline="0" capitalization="0" namedStyle="Normale" fontStrikeout="0" fontSizeUnit="Point" fontWeight="50" fontSize="7" fieldName="particella" previewBkgrdColor="255,255,255,255" fontItalic="0" fontKerning="1" isExpression="0" textOpacity="1" allowHtml="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" useSubstitutions="0" textOrientation="horizontal" blendMode="0" textColor="22,22,166,255" fontFamily="MS Shell Dlg 2">
        <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferJoinStyle="128" bufferDraw="0" bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="255,255,255,255" bufferSize="1" bufferNoFill="1" bufferOpacity="1"/>
        <text-mask maskEnabled="0" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSizeUnits="MM" maskOpacity="1" maskType="0" maskJoinStyle="128" maskedSymbolLayers=""/>
        <background shapeSizeY="0" shapeSVGFile="" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeFillColor="255,255,255,255" shapeRadiiY="0" shapeBlendMode="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeBorderColor="128,128,128,255" shapeOffsetX="0" shapeRadiiUnit="MM" shapeBorderWidthUnit="MM" shapeBorderWidth="0" shapeOffsetY="0" shapeRotationType="0" shapeSizeType="0" shapeOpacity="1" shapeJoinStyle="64" shapeRotation="0" shapeSizeUnit="MM">
          <symbol name="markerSymbol" alpha="1" type="marker" force_rhr="0" clip_to_extent="1">
            <layer class="SimpleMarker" locked="0" enabled="1" pass="0">
              <prop v="0" k="angle"/>
              <prop v="213,180,60,255" k="color"/>
              <prop v="1" k="horizontal_anchor_point"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="circle" k="name"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="35,35,35,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="diameter" k="scale_method"/>
              <prop v="2" k="size"/>
              <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
              <prop v="MM" k="size_unit"/>
              <prop v="1" k="vertical_anchor_point"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowScale="100" shadowOffsetUnit="MM" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowBlendMode="6" shadowUnder="0" shadowColor="0,0,0,255" shadowDraw="0" shadowRadius="1.5" shadowRadiusUnit="MM" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetDist="1" shadowOpacity="0.7"/>
        <dd_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format autoWrapLength="0" multilineAlign="3" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" addDirectionSymbol="0" plussign="0" formatNumbers="0" wrapChar="" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1" placeDirectionSymbol="0" decimals="3"/>
      <placement predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" preserveRotation="1" fitInPolygonOnly="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" placement="0" layerType="PolygonGeometry" polygonPlacementFlags="2" geometryGenerator="" rotationAngle="0" repeatDistanceUnits="MM" lineAnchorPercent="0.5" quadOffset="4" geometryGeneratorEnabled="0" xOffset="0" maxCurvedCharAngleIn="25" distUnits="MM" maxCurvedCharAngleOut="-25" yOffset="0" centroidWhole="0" priority="5" geometryGeneratorType="PointGeometry" centroidInside="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" overrunDistance="0" dist="0" repeatDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MM" overrunDistanceUnit="MM" lineAnchorType="0"/>
      <rendering fontMaxPixelSize="10000" minFeatureSize="0" scaleMax="0" fontLimitPixelSize="0" scaleVisibility="0" maxNumLabels="2000" mergeLines="0" upsidedownLabels="0" obstacleType="1" displayAll="0" labelPerPart="0" drawLabels="1" obstacleFactor="1" limitNumLabels="0" obstacle="1" fontMinPixelSize="3" zIndex="0" scaleMin="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
          <Option name="ddProperties" type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
          <Option value="false" name="drawToAllParts" type="bool"/>
          <Option value="0" name="enabled" type="QString"/>
          <Option value="point_on_exterior" name="labelAnchorPoint" type="QString"/>
          <Option value="&lt;symbol name=&quot;symbol&quot; alpha=&quot;1&quot; type=&quot;line&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; locked=&quot;0&quot; enabled=&quot;1&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol" type="QString"/>
          <Option value="0" name="minLength" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale" type="QString"/>
          <Option value="MM" name="minLengthUnit" type="QString"/>
          <Option value="0" name="offsetFromAnchor" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromAnchorUnit" type="QString"/>
          <Option value="0" name="offsetFromLabel" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromLabelUnit" type="QString"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
