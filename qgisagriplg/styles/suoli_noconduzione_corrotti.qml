<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="1" version="3.16.16-Hannover" styleCategories="Symbology|Labeling">
  <renderer-v2 forceraster="0" symbollevels="0" enableorderby="0" type="RuleRenderer">
    <rules key="{c3b5cf28-0b0c-4dbd-a019-a6c2bdcd9983}">
      <rule filter="&quot;flagLavorato&quot; = 1" key="{758a1c81-5a73-491f-b571-04025f314e88}" label="Modificati" symbol="0"/>
      <rule filter="&quot;flagLavorato&quot; != 1" key="{6400c681-1ab8-48cd-809c-13d2b13bd507}" label="Non modificati" symbol="1"/>
      <rule filter=" &quot;flagControlloCampo&quot; = 'S'" checkstate="0" description="zzzzzz" key="{bb6b61f5-30c7-4817-9edc-e0c499263497}" label="Controllato in campo" symbol="2"/>
      <rule checkstate="0" key="{d7c9b0ed-5b57-4fdf-a34a-06de1952ea86}" label="Evidenzia vertici" symbol="3"/>
    </rules>
    <symbols>
      <symbol name="0" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.669">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="168,155,155,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diagonal_x" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="121,112,112,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="121,112,112,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="3" k="outline_width"/>
          <prop v="Point" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="252,148,137,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="1" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="121,112,112,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="136,9,140,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="3" k="outline_width"/>
          <prop v="Point" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="121,112,112,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="2" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="SimpleLine" enabled="1" pass="10" locked="0">
          <prop v="0" k="align_dash_pattern"/>
          <prop v="square" k="capstyle"/>
          <prop v="1;5" k="customdash"/>
          <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
          <prop v="MM" k="customdash_unit"/>
          <prop v="0" k="dash_pattern_offset"/>
          <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
          <prop v="MM" k="dash_pattern_offset_unit"/>
          <prop v="0" k="draw_inside_polygon"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="88,140,5,255" k="line_color"/>
          <prop v="dot" k="line_style"/>
          <prop v="1.96" k="line_width"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0" k="ring_filter"/>
          <prop v="0" k="tweak_dash_pattern_on_corners"/>
          <prop v="1" k="use_custom_dash"/>
          <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="3" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="MarkerLine" enabled="1" pass="20" locked="0">
          <prop v="4" k="average_angle_length"/>
          <prop v="3x:0,0,0,0,0,0" k="average_angle_map_unit_scale"/>
          <prop v="MM" k="average_angle_unit"/>
          <prop v="3" k="interval"/>
          <prop v="3x:0,0,0,0,0,0" k="interval_map_unit_scale"/>
          <prop v="MM" k="interval_unit"/>
          <prop v="0" k="offset"/>
          <prop v="0" k="offset_along_line"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_along_line_map_unit_scale"/>
          <prop v="MM" k="offset_along_line_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="vertex" k="placement"/>
          <prop v="0" k="ring_filter"/>
          <prop v="0" k="rotate"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@3@0" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
            <layer class="SimpleMarker" enabled="1" pass="0" locked="0">
              <prop v="0" k="angle"/>
              <prop v="0,0,0,255" k="color"/>
              <prop v="1" k="horizontal_anchor_point"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="circle" k="name"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="255,255,255,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0.4" k="outline_width"/>
              <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="diameter" k="scale_method"/>
              <prop v="2" k="size"/>
              <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
              <prop v="MM" k="size_unit"/>
              <prop v="1" k="vertical_anchor_point"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="rule-based">
    <rules key="{e0ab2a82-6e44-4a4e-98ab-54329f73e102}">
      <rule scalemindenom="1" description="Eleggibilità" key="{2fd799d2-5a79-4810-adb5-63412267c234}" scalemaxdenom="100000">
        <settings calloutType="simple">
          <text-style fontFamily="MS Shell Dlg 2" blendMode="0" fieldName="codiceEleggibilitaRilevata" previewBkgrdColor="255,255,255,255" namedStyle="Normale" textOpacity="1" fontItalic="0" textOrientation="horizontal" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSize="10" textColor="0,0,0,255" fontLetterSpacing="0" fontWeight="50" allowHtml="0" fontStrikeout="0" fontWordSpacing="0" fontKerning="1" fontSizeUnit="Point" fontUnderline="0" isExpression="0" capitalization="0" useSubstitutions="0" multilineHeight="1">
            <text-buffer bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="213,211,211,255" bufferOpacity="0.313" bufferDraw="1" bufferJoinStyle="128" bufferSize="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1">
              <effect enabled="1" type="effectStack">
                <effect type="dropShadow">
                  <prop v="13" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="outerGlow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="0.7935" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,255,255" k="color1"/>
                  <prop v="0,255,0,255" k="color2"/>
                  <prop v="0" k="color_type"/>
                  <prop v="0" k="discrete"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="0.5" k="opacity"/>
                  <prop v="gradient" k="rampType"/>
                  <prop v="255,255,255,255" k="single_color"/>
                  <prop v="2" k="spread"/>
                  <prop v="MM" k="spread_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
                </effect>
                <effect type="drawSource">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="innerShadow">
                  <prop v="13" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="innerGlow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="0.7935" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,255,255" k="color1"/>
                  <prop v="0,255,0,255" k="color2"/>
                  <prop v="0" k="color_type"/>
                  <prop v="0" k="discrete"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="0.5" k="opacity"/>
                  <prop v="gradient" k="rampType"/>
                  <prop v="255,255,255,255" k="single_color"/>
                  <prop v="2" k="spread"/>
                  <prop v="MM" k="spread_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
                </effect>
              </effect>
            </text-buffer>
            <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="0" maskEnabled="0" maskJoinStyle="128" maskType="0" maskSizeUnits="MM" maskedSymbolLayers="" maskOpacity="1"/>
            <background shapeOffsetY="0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeBorderWidth="0" shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="230,228,228,255" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeSizeType="0" shapeBorderColor="128,128,128,255" shapeBorderWidthUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeDraw="1" shapeSizeX="0" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="64" shapeType="0" shapeRotationType="0" shapeBlendMode="0" shapeSizeY="0" shapeOffsetX="0">
              <symbol name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
                <layer class="SimpleMarker" enabled="1" pass="0" locked="0">
                  <prop v="0" k="angle"/>
                  <prop v="232,113,141,255" k="color"/>
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
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetUnit="MM" shadowRadius="1.5" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowDraw="0" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowUnder="0" shadowBlendMode="6" shadowOffsetDist="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format formatNumbers="0" wrapChar="" autoWrapLength="0" plussign="0" multilineAlign="0" useMaxLineLengthForAutoWrap="1" decimals="3" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" preserveRotation="1" xOffset="0" lineAnchorPercent="0.5" centroidInside="1" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" yOffset="0" overrunDistanceUnit="MM" offsetType="0" geometryGenerator="" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placement="0" layerType="PolygonGeometry" maxCurvedCharAngleOut="-25" maxCurvedCharAngleIn="25" fitInPolygonOnly="0" centroidWhole="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" distMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" rotationAngle="0" offsetUnits="MM" repeatDistance="0" geometryGeneratorType="PointGeometry" quadOffset="4" overrunDistance="0" dist="0" priority="5" lineAnchorType="0" distUnits="MM"/>
          <rendering scaleVisibility="0" obstacleFactor="0" maxNumLabels="2000" labelPerPart="0" scaleMax="0" scaleMin="0" obstacle="1" displayAll="0" upsidedownLabels="0" limitNumLabels="0" minFeatureSize="0" fontMaxPixelSize="10000" drawLabels="1" zIndex="0" fontLimitPixelSize="0" fontMinPixelSize="3" obstacleType="0" mergeLines="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; pass=&quot;0&quot; locked=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule scalemindenom="1" description="Note richiesta" key="{79e1e623-c454-48c4-8cdf-0bf2527a9283}" scalemaxdenom="100000">
        <settings calloutType="simple">
          <text-style fontFamily="MS Shell Dlg 2" blendMode="0" fieldName="if(length(coalesce(&quot;note&quot;, '')) > 50, left(coalesce(&quot;note&quot;, ''), 50 ) + '...', &quot;note&quot;)&#xd;" previewBkgrdColor="255,255,255,255" namedStyle="Normale" textOpacity="1" fontItalic="0" textOrientation="horizontal" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSize="10" textColor="0,0,0,255" fontLetterSpacing="0" fontWeight="50" allowHtml="0" fontStrikeout="0" fontWordSpacing="0" fontKerning="1" fontSizeUnit="Point" fontUnderline="0" isExpression="1" capitalization="0" useSubstitutions="0" multilineHeight="1">
            <text-buffer bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="221,221,221,255" bufferOpacity="1" bufferDraw="1" bufferJoinStyle="128" bufferSize="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1"/>
            <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="0" maskEnabled="0" maskJoinStyle="128" maskType="0" maskSizeUnits="MM" maskedSymbolLayers="" maskOpacity="1"/>
            <background shapeOffsetY="0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeBorderWidth="0" shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeSizeType="0" shapeBorderColor="128,128,128,255" shapeBorderWidthUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeDraw="0" shapeSizeX="0" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="64" shapeType="0" shapeRotationType="0" shapeBlendMode="0" shapeSizeY="0" shapeOffsetX="0">
              <symbol name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
                <layer class="SimpleMarker" enabled="1" pass="0" locked="0">
                  <prop v="0" k="angle"/>
                  <prop v="190,178,151,255" k="color"/>
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
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetUnit="MM" shadowRadius="1.5" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowDraw="1" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowUnder="0" shadowBlendMode="6" shadowOffsetDist="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format formatNumbers="0" wrapChar="" autoWrapLength="0" plussign="0" multilineAlign="0" useMaxLineLengthForAutoWrap="1" decimals="3" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" preserveRotation="1" xOffset="0" lineAnchorPercent="0.5" centroidInside="1" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" yOffset="0" overrunDistanceUnit="MM" offsetType="0" geometryGenerator="" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placement="0" layerType="PolygonGeometry" maxCurvedCharAngleOut="-25" maxCurvedCharAngleIn="25" fitInPolygonOnly="0" centroidWhole="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" distMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" rotationAngle="0" offsetUnits="MM" repeatDistance="0" geometryGeneratorType="PointGeometry" quadOffset="4" overrunDistance="0" dist="4" priority="5" lineAnchorType="0" distUnits="MM"/>
          <rendering scaleVisibility="0" obstacleFactor="0.7" maxNumLabels="2000" labelPerPart="1" scaleMax="0" scaleMin="0" obstacle="0" displayAll="1" upsidedownLabels="0" limitNumLabels="0" minFeatureSize="0" fontMaxPixelSize="10000" drawLabels="1" zIndex="0" fontLimitPixelSize="0" fontMinPixelSize="3" obstacleType="0" mergeLines="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; pass=&quot;0&quot; locked=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule scalemindenom="1" description="Note lavorazione" key="{4444e913-a6bd-452c-9c86-e55b65830fa6}" scalemaxdenom="100000">
        <settings calloutType="simple">
          <text-style fontFamily="MS Shell Dlg 2" blendMode="0" fieldName="if(length(coalesce(&quot;noteLavorazione&quot;, '')) > 50, left(coalesce(&quot;noteLavorazione&quot;, ''), 50 ) + '...', &quot;noteLavorazione&quot;)" previewBkgrdColor="255,255,255,255" namedStyle="Normale" textOpacity="1" fontItalic="0" textOrientation="horizontal" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSize="10" textColor="0,0,0,255" fontLetterSpacing="0" fontWeight="50" allowHtml="0" fontStrikeout="0" fontWordSpacing="0" fontKerning="1" fontSizeUnit="Point" fontUnderline="0" isExpression="1" capitalization="0" useSubstitutions="0" multilineHeight="1">
            <text-buffer bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="255,255,255,255" bufferOpacity="1" bufferDraw="1" bufferJoinStyle="128" bufferSize="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1"/>
            <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="0" maskEnabled="0" maskJoinStyle="128" maskType="0" maskSizeUnits="MM" maskedSymbolLayers="" maskOpacity="1"/>
            <background shapeOffsetY="0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeBorderWidth="0" shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeSizeType="0" shapeBorderColor="128,128,128,255" shapeBorderWidthUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeDraw="0" shapeSizeX="0" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="64" shapeType="0" shapeRotationType="0" shapeBlendMode="0" shapeSizeY="0" shapeOffsetX="0">
              <symbol name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
                <layer class="SimpleMarker" enabled="1" pass="0" locked="0">
                  <prop v="0" k="angle"/>
                  <prop v="196,60,57,255" k="color"/>
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
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetUnit="MM" shadowRadius="1.5" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowDraw="1" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowUnder="0" shadowBlendMode="6" shadowOffsetDist="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format formatNumbers="0" wrapChar="" autoWrapLength="0" plussign="0" multilineAlign="0" useMaxLineLengthForAutoWrap="1" decimals="3" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" preserveRotation="1" xOffset="0" lineAnchorPercent="0.5" centroidInside="1" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" yOffset="0" overrunDistanceUnit="MM" offsetType="0" geometryGenerator="" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placement="0" layerType="PolygonGeometry" maxCurvedCharAngleOut="-25" maxCurvedCharAngleIn="25" fitInPolygonOnly="0" centroidWhole="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" distMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" rotationAngle="0" offsetUnits="MM" repeatDistance="0" geometryGeneratorType="PointGeometry" quadOffset="4" overrunDistance="0" dist="4" priority="5" lineAnchorType="0" distUnits="MM"/>
          <rendering scaleVisibility="0" obstacleFactor="1" maxNumLabels="2000" labelPerPart="0" scaleMax="0" scaleMin="0" obstacle="1" displayAll="1" upsidedownLabels="0" limitNumLabels="0" minFeatureSize="0" fontMaxPixelSize="10000" drawLabels="1" zIndex="0" fontLimitPixelSize="0" fontMinPixelSize="3" obstacleType="0" mergeLines="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; pass=&quot;0&quot; locked=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule scalemindenom="1" description="Descrizione sospensione" key="{021e4e65-e8f0-46e3-af52-a8fdac2461e6}" scalemaxdenom="100000">
        <settings calloutType="simple">
          <text-style fontFamily="MS Shell Dlg 2" blendMode="0" fieldName="if(length(coalesce(&quot;descrizioneSospensione&quot;, '')) > 50, left(coalesce(&quot;descrizioneSospensione&quot;, ''), 50 ) + '...', &quot;descrizioneSospensione&quot;)" previewBkgrdColor="255,255,255,255" namedStyle="Normale" textOpacity="1" fontItalic="0" textOrientation="horizontal" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSize="10" textColor="0,0,0,255" fontLetterSpacing="0" fontWeight="50" allowHtml="0" fontStrikeout="0" fontWordSpacing="0" fontKerning="1" fontSizeUnit="Point" fontUnderline="0" isExpression="1" capitalization="0" useSubstitutions="0" multilineHeight="1">
            <text-buffer bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="255,255,139,255" bufferOpacity="1" bufferDraw="1" bufferJoinStyle="128" bufferSize="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1"/>
            <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="0" maskEnabled="0" maskJoinStyle="128" maskType="0" maskSizeUnits="MM" maskedSymbolLayers="" maskOpacity="1"/>
            <background shapeOffsetY="0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeBorderWidth="0" shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeSizeType="0" shapeBorderColor="128,128,128,255" shapeBorderWidthUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeDraw="0" shapeSizeX="0" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="64" shapeType="0" shapeRotationType="0" shapeBlendMode="0" shapeSizeY="0" shapeOffsetX="0">
              <symbol name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
                <layer class="SimpleMarker" enabled="1" pass="0" locked="0">
                  <prop v="0" k="angle"/>
                  <prop v="229,182,54,255" k="color"/>
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
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetUnit="MM" shadowRadius="1.5" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowDraw="1" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowUnder="0" shadowBlendMode="6" shadowOffsetDist="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format formatNumbers="0" wrapChar="" autoWrapLength="0" plussign="0" multilineAlign="0" useMaxLineLengthForAutoWrap="1" decimals="3" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" preserveRotation="1" xOffset="0" lineAnchorPercent="0.5" centroidInside="1" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" yOffset="0" overrunDistanceUnit="MM" offsetType="0" geometryGenerator="" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placement="0" layerType="PolygonGeometry" maxCurvedCharAngleOut="-25" maxCurvedCharAngleIn="25" fitInPolygonOnly="0" centroidWhole="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" distMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" rotationAngle="0" offsetUnits="MM" repeatDistance="0" geometryGeneratorType="PointGeometry" quadOffset="4" overrunDistance="0" dist="4" priority="5" lineAnchorType="0" distUnits="MM"/>
          <rendering scaleVisibility="0" obstacleFactor="1" maxNumLabels="2000" labelPerPart="0" scaleMax="0" scaleMin="0" obstacle="1" displayAll="1" upsidedownLabels="0" limitNumLabels="0" minFeatureSize="0" fontMaxPixelSize="10000" drawLabels="1" zIndex="0" fontLimitPixelSize="0" fontMinPixelSize="3" obstacleType="0" mergeLines="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; pass=&quot;0&quot; locked=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
      <rule active="0" scalemindenom="1" description="Area" key="{7629ebee-d225-4158-906e-818f8ccf8aef}" scalemaxdenom="3000">
        <settings calloutType="simple">
          <text-style fontFamily="MS Shell Dlg 2" blendMode="0" fieldName="format_number(area($geometry),2) + ' m²'" previewBkgrdColor="74,74,74,255" namedStyle="Normale" textOpacity="1" fontItalic="0" textOrientation="horizontal" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSize="8" textColor="255,255,255,255" fontLetterSpacing="0" fontWeight="50" allowHtml="0" fontStrikeout="0" fontWordSpacing="0" fontKerning="1" fontSizeUnit="Point" fontUnderline="0" isExpression="1" capitalization="0" useSubstitutions="0" multilineHeight="1">
            <text-buffer bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="255,255,255,255" bufferOpacity="1" bufferDraw="0" bufferJoinStyle="128" bufferSize="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1"/>
            <text-mask maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="0" maskEnabled="0" maskJoinStyle="128" maskType="0" maskSizeUnits="MM" maskedSymbolLayers="" maskOpacity="1"/>
            <background shapeOffsetY="0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeBorderWidth="1" shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="74,74,74,255" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeSizeType="0" shapeBorderColor="74,74,74,255" shapeBorderWidthUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeDraw="1" shapeSizeX="0" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="128" shapeType="0" shapeRotationType="0" shapeBlendMode="0" shapeSizeY="0" shapeOffsetX="0">
              <effect enabled="1" type="effectStack">
                <effect type="dropShadow">
                  <prop v="13" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="outerGlow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,255,255" k="color1"/>
                  <prop v="0,255,0,255" k="color2"/>
                  <prop v="0" k="color_type"/>
                  <prop v="0" k="discrete"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="0" k="enabled"/>
                  <prop v="0.5" k="opacity"/>
                  <prop v="gradient" k="rampType"/>
                  <prop v="255,255,255,255" k="single_color"/>
                  <prop v="2" k="spread"/>
                  <prop v="MM" k="spread_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
                </effect>
                <effect type="drawSource">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="1" k="enabled"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="innerShadow">
                  <prop v="13" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,0,255" k="color"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="0" k="enabled"/>
                  <prop v="135" k="offset_angle"/>
                  <prop v="2" k="offset_distance"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_unit_scale"/>
                  <prop v="1" k="opacity"/>
                </effect>
                <effect type="innerGlow">
                  <prop v="0" k="blend_mode"/>
                  <prop v="2.645" k="blur_level"/>
                  <prop v="MM" k="blur_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="blur_unit_scale"/>
                  <prop v="0,0,255,255" k="color1"/>
                  <prop v="0,255,0,255" k="color2"/>
                  <prop v="0" k="color_type"/>
                  <prop v="0" k="discrete"/>
                  <prop v="2" k="draw_mode"/>
                  <prop v="0" k="enabled"/>
                  <prop v="0.5" k="opacity"/>
                  <prop v="gradient" k="rampType"/>
                  <prop v="255,255,255,255" k="single_color"/>
                  <prop v="2" k="spread"/>
                  <prop v="MM" k="spread_unit"/>
                  <prop v="3x:0,0,0,0,0,0" k="spread_unit_scale"/>
                </effect>
              </effect>
              <symbol name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
                <layer class="SimpleMarker" enabled="1" pass="0" locked="0">
                  <prop v="0" k="angle"/>
                  <prop v="190,207,80,255" k="color"/>
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
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetUnit="MM" shadowRadius="1.5" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowDraw="0" shadowOpacity="0.7" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowUnder="0" shadowBlendMode="6" shadowOffsetDist="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format formatNumbers="0" wrapChar="" autoWrapLength="0" plussign="0" multilineAlign="0" useMaxLineLengthForAutoWrap="1" decimals="3" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" placeDirectionSymbol="0" rightDirectionSymbol=">" addDirectionSymbol="0"/>
          <placement polygonPlacementFlags="2" preserveRotation="1" xOffset="0" lineAnchorPercent="0.5" centroidInside="0" repeatDistanceUnits="MM" geometryGeneratorEnabled="0" yOffset="0" overrunDistanceUnit="MM" offsetType="0" geometryGenerator="" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placement="0" layerType="PolygonGeometry" maxCurvedCharAngleOut="-25" maxCurvedCharAngleIn="25" fitInPolygonOnly="0" centroidWhole="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" distMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" rotationAngle="0" offsetUnits="MM" repeatDistance="0" geometryGeneratorType="PointGeometry" quadOffset="4" overrunDistance="0" dist="4" priority="5" lineAnchorType="0" distUnits="MM"/>
          <rendering scaleVisibility="0" obstacleFactor="1" maxNumLabels="2000" labelPerPart="0" scaleMax="0" scaleMin="0" obstacle="0" displayAll="1" upsidedownLabels="0" limitNumLabels="0" minFeatureSize="0" fontMaxPixelSize="10000" drawLabels="1" zIndex="0" fontLimitPixelSize="0" fontMinPixelSize="3" obstacleType="0" mergeLines="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="labelAnchorPoint" type="QString" value="point_on_exterior"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer class=&quot;SimpleLine&quot; enabled=&quot;1&quot; pass=&quot;0&quot; locked=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </rule>
    </rules>
  </labeling>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
