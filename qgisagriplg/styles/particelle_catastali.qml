<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology|Labeling|Fields|Forms" version="3.16.16-Hannover" labelsEnabled="1">
  <renderer-v2 forceraster="0" type="RuleRenderer" enableorderby="0" symbollevels="0">
    <rules key="{c7dcee8c-9db0-4664-b029-26f3b3912ce8}">
      <rule filter="&quot;flagConduzione&quot; = 'S'" key="{4d421288-3a6a-49ef-bc2f-cf8d89d9e5a1}" symbol="0" label="Particelle in conduzione">
        <rule filter="&quot;flagLavorato&quot; = 1" key="{4ab6b12b-f7c6-4934-b58d-32ba5dc04ad0}" symbol="1" label="Modificati"/>
      </rule>
      <rule filter="&quot;flagConduzione&quot; != 'S'" key="{762c881e-8a9d-49af-aaab-e8f1bab5204e}" symbol="2" label="Particelle non in conduzione">
        <rule filter="&quot;flagLavorato&quot; = 1" key="{dc990eb3-95cf-4c43-bf1d-27c33f4c8a6f}" symbol="3" label="Modificati"/>
      </rule>
      <rule key="{645334aa-dfeb-43e8-a4fd-86570d3ad4ae}" symbol="4" label="Particelle editabili">
        <rule filter="isEditedFeature( @layer_id )" key="{1b235178-c1bc-412e-b6c0-5dff6378849f}" symbol="5" label="Particelle editate"/>
      </rule>
      <rule filter="&quot;_flagInvalido&quot;  = 1" key="{f783796c-a15c-4cc0-b08b-5b860f8e71e9}" symbol="6" label="Invalide"/>
      <rule checkstate="0" key="{db75129a-c612-4218-ad54-eed151a69a52}" symbol="7" label="Evidenzia vertici"/>
    </rules>
    <symbols>
      <symbol name="0" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer locked="0" enabled="1" class="SimpleFill" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="0,162,232,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
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
        <layer locked="0" enabled="1" class="SimpleFill" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="16,0,248,255" k="color"/>
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
      </symbol>
      <symbol name="2" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer locked="0" enabled="1" class="SimpleFill" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="248,224,6,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="3" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer locked="0" enabled="1" class="SimpleFill" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="16,0,248,255" k="color"/>
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
      </symbol>
      <symbol name="4" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer locked="0" enabled="1" class="SimpleFill" pass="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="0,0,255,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
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
      <symbol name="5" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer locked="0" enabled="1" class="GradientFill" pass="0">
          <prop v="0" k="angle"/>
          <prop v="200,185,185,255" k="color"/>
          <prop v="0,0,255,255" k="color1"/>
          <prop v="0,255,0,255" k="color2"/>
          <prop v="0" k="color_type"/>
          <prop v="0" k="coordinate_mode"/>
          <prop v="0" k="discrete"/>
          <prop v="255,255,255,255" k="gradient_color2"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="gradient" k="rampType"/>
          <prop v="0.5,0" k="reference_point1"/>
          <prop v="0" k="reference_point1_iscentroid"/>
          <prop v="0.5,1" k="reference_point2"/>
          <prop v="0" k="reference_point2_iscentroid"/>
          <prop v="0" k="spread"/>
          <prop v="0" k="type"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="6" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer locked="0" enabled="1" class="CentroidFill" pass="0">
          <prop v="0" k="clip_on_current_part_only"/>
          <prop v="0" k="clip_points"/>
          <prop v="1" k="point_on_all_parts"/>
          <prop v="1" k="point_on_surface"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol name="@6@0" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
            <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
              <prop v="0" k="angle"/>
              <prop v="240,255,182,255" k="color"/>
              <prop v="1" k="horizontal_anchor_point"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="triangle" k="name"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="255,53,0,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0.4" k="outline_width"/>
              <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="diameter" k="scale_method"/>
              <prop v="4" k="size"/>
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
      <symbol name="7" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer locked="0" enabled="1" class="MarkerLine" pass="0">
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
          <symbol name="@7@0" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
            <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
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
    <rules key="{b46c7f40-d0fc-47f5-ab49-e4ba77e4f41f}">
      <rule key="{170f0f21-cdc0-4d84-ad46-c1df929d8948}" description="Mappale">
        <settings calloutType="simple">
          <text-style capitalization="0" isExpression="0" fontSizeUnit="Point" textColor="0,0,0,255" multilineHeight="1" fontLetterSpacing="0" allowHtml="0" fontFamily="MS Shell Dlg 2" blendMode="0" fontWordSpacing="0" fontSize="10" fieldName="numeroParticella" fontWeight="50" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontKerning="1" fontItalic="0" textOrientation="horizontal" fontStrikeout="0" previewBkgrdColor="0,0,0,255" namedStyle="Normale" textOpacity="1" fontUnderline="0" useSubstitutions="0">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0" bufferSize="1" bufferColor="255,255,255,255" bufferOpacity="1" bufferJoinStyle="128" bufferSizeUnits="MM" bufferNoFill="1" bufferDraw="0"/>
            <text-mask maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskOpacity="1" maskedSymbolLayers="" maskType="0" maskSizeUnits="MM" maskEnabled="0" maskJoinStyle="128"/>
            <background shapeRotationType="0" shapeJoinStyle="0" shapeBorderWidthUnit="MM" shapeDraw="1" shapeSVGFile="" shapeBorderColor="71,103,231,255" shapeOffsetUnit="MM" shapeSizeUnit="MM" shapeFillColor="71,103,231,255" shapeSizeX="0" shapeOffsetX="-0.4" shapeRadiiY="0" shapeSizeType="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeRadiiX="0" shapeSizeY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidth="1" shapeBlendMode="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeType="0" shapeRadiiUnit="MM">
              <symbol name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
                <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
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
            <shadow shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowDraw="0" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowOpacity="0.7" shadowBlendMode="6" shadowUnder="0" shadowRadiusUnit="MM" shadowOffsetDist="1" shadowRadius="1.5" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format addDirectionSymbol="0" formatNumbers="0" wrapChar="" multilineAlign="0" reverseDirectionSymbol="0" decimals="3" rightDirectionSymbol=">" autoWrapLength="0" plussign="0" useMaxLineLengthForAutoWrap="1" leftDirectionSymbol="&lt;" placeDirectionSymbol="0"/>
          <placement layerType="PolygonGeometry" lineAnchorType="0" offsetUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" rotationAngle="0" geometryGeneratorEnabled="0" dist="0" repeatDistanceUnits="MM" quadOffset="4" fitInPolygonOnly="0" offsetType="0" centroidInside="1" yOffset="0" polygonPlacementFlags="2" xOffset="0" distMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" priority="5" lineAnchorPercent="0.5" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" maxCurvedCharAngleIn="25" placementFlags="10" overrunDistanceUnit="MM" geometryGeneratorType="PointGeometry" distUnits="MM" geometryGenerator="" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" placement="0" maxCurvedCharAngleOut="-25"/>
          <rendering minFeatureSize="0" fontLimitPixelSize="0" obstacleType="0" labelPerPart="0" obstacleFactor="1" displayAll="0" limitNumLabels="0" fontMinPixelSize="3" drawLabels="1" maxNumLabels="2000" zIndex="0" upsidedownLabels="0" scaleMin="0" scaleMax="0" mergeLines="0" scaleVisibility="0" obstacle="1" fontMaxPixelSize="10000"/>
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
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer locked=&quot;0&quot; enabled=&quot;1&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
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
      <rule scalemaxdenom="3000" scalemindenom="1" key="{9f5f783f-11d4-4eec-a730-e6252f5b10bb}" active="0" description="Area">
        <settings calloutType="simple">
          <text-style capitalization="0" isExpression="1" fontSizeUnit="Point" textColor="0,0,0,255" multilineHeight="1" fontLetterSpacing="0" allowHtml="0" fontFamily="MS Shell Dlg 2" blendMode="0" fontWordSpacing="0" fontSize="8" fieldName="format_number(area($geometry),2) + ' m²'" fontWeight="50" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontKerning="1" fontItalic="0" textOrientation="horizontal" fontStrikeout="0" previewBkgrdColor="0,0,0,255" namedStyle="Normale" textOpacity="1" fontUnderline="0" useSubstitutions="0">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0" bufferSize="1" bufferColor="255,255,255,255" bufferOpacity="1" bufferJoinStyle="128" bufferSizeUnits="MM" bufferNoFill="1" bufferDraw="0"/>
            <text-mask maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskOpacity="1" maskedSymbolLayers="" maskType="0" maskSizeUnits="MM" maskEnabled="0" maskJoinStyle="128"/>
            <background shapeRotationType="0" shapeJoinStyle="128" shapeBorderWidthUnit="MM" shapeDraw="1" shapeSVGFile="" shapeBorderColor="0,144,206,255" shapeOffsetUnit="MM" shapeSizeUnit="MM" shapeFillColor="0,144,206,255" shapeSizeX="0" shapeOffsetX="0" shapeRadiiY="0" shapeSizeType="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeRadiiX="0" shapeSizeY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidth="1" shapeBlendMode="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeType="0" shapeRadiiUnit="MM">
              <effect type="effectStack" enabled="1">
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
            </background>
            <shadow shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowDraw="0" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowOpacity="0.7" shadowBlendMode="6" shadowUnder="0" shadowRadiusUnit="MM" shadowOffsetDist="1" shadowRadius="1.5" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties" type="Map">
                  <Option name="Show" type="Map">
                    <Option name="active" type="bool" value="true"/>
                    <Option name="expression" type="QString" value="&quot;flagConduzione&quot; = 'S'"/>
                    <Option name="type" type="int" value="3"/>
                  </Option>
                </Option>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format addDirectionSymbol="0" formatNumbers="0" wrapChar="" multilineAlign="0" reverseDirectionSymbol="0" decimals="3" rightDirectionSymbol=">" autoWrapLength="0" plussign="0" useMaxLineLengthForAutoWrap="1" leftDirectionSymbol="&lt;" placeDirectionSymbol="0"/>
          <placement layerType="UnknownGeometry" lineAnchorType="0" offsetUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" rotationAngle="0" geometryGeneratorEnabled="0" dist="4" repeatDistanceUnits="MM" quadOffset="4" fitInPolygonOnly="0" offsetType="0" centroidInside="0" yOffset="0" polygonPlacementFlags="2" xOffset="0" distMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" priority="5" lineAnchorPercent="0.5" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" maxCurvedCharAngleIn="25" placementFlags="10" overrunDistanceUnit="MM" geometryGeneratorType="PointGeometry" distUnits="MM" geometryGenerator="" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" placement="0" maxCurvedCharAngleOut="-25"/>
          <rendering minFeatureSize="0" fontLimitPixelSize="0" obstacleType="0" labelPerPart="0" obstacleFactor="1" displayAll="1" limitNumLabels="0" fontMinPixelSize="3" drawLabels="1" maxNumLabels="2000" zIndex="0" upsidedownLabels="0" scaleMin="0" scaleMax="0" mergeLines="0" scaleVisibility="0" obstacle="0" fontMaxPixelSize="10000"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="Show" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="&quot;flagConduzione&quot; = 'S'"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
              </Option>
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
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer locked=&quot;0&quot; enabled=&quot;1&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
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
      <rule scalemaxdenom="100000" scalemindenom="1" key="{e49b449d-390a-4e02-bb89-b31abd963a0e}" description="Descrizione sospensione">
        <settings calloutType="simple">
          <text-style capitalization="0" isExpression="1" fontSizeUnit="Point" textColor="0,0,0,255" multilineHeight="1" fontLetterSpacing="0" allowHtml="0" fontFamily="MS Shell Dlg 2" blendMode="0" fontWordSpacing="0" fontSize="10" fieldName="if(length(coalesce(&quot;descrizioneSospensione&quot;, '')) > 50, left(coalesce(&quot;descrizioneSospensione&quot;, ''), 50 ) + '...', &quot;descrizioneSospensione&quot;)" fontWeight="50" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontKerning="1" fontItalic="0" textOrientation="horizontal" fontStrikeout="0" previewBkgrdColor="255,255,255,255" namedStyle="Normale" textOpacity="1" fontUnderline="0" useSubstitutions="0">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0" bufferSize="1" bufferColor="8,206,255,255" bufferOpacity="1" bufferJoinStyle="128" bufferSizeUnits="MM" bufferNoFill="1" bufferDraw="1"/>
            <text-mask maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskOpacity="1" maskedSymbolLayers="" maskType="0" maskSizeUnits="MM" maskEnabled="0" maskJoinStyle="128"/>
            <background shapeRotationType="0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeDraw="0" shapeSVGFile="" shapeBorderColor="128,128,128,255" shapeOffsetUnit="MM" shapeSizeUnit="MM" shapeFillColor="255,255,255,255" shapeSizeX="0" shapeOffsetX="0" shapeRadiiY="0" shapeSizeType="0" shapeRotation="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeRadiiX="0" shapeSizeY="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidth="0" shapeBlendMode="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeType="0" shapeRadiiUnit="MM">
              <symbol name="markerSymbol" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
                <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
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
            <shadow shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowDraw="1" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowOpacity="0.7" shadowBlendMode="6" shadowUnder="0" shadowRadiusUnit="MM" shadowOffsetDist="1" shadowRadius="1.5" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowScale="100" shadowOffsetUnit="MM"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format addDirectionSymbol="0" formatNumbers="0" wrapChar="" multilineAlign="0" reverseDirectionSymbol="0" decimals="3" rightDirectionSymbol=">" autoWrapLength="0" plussign="0" useMaxLineLengthForAutoWrap="1" leftDirectionSymbol="&lt;" placeDirectionSymbol="0"/>
          <placement layerType="PolygonGeometry" lineAnchorType="0" offsetUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" rotationAngle="0" geometryGeneratorEnabled="0" dist="4" repeatDistanceUnits="MM" quadOffset="4" fitInPolygonOnly="0" offsetType="0" centroidInside="1" yOffset="0" polygonPlacementFlags="2" xOffset="0" distMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" priority="5" lineAnchorPercent="0.5" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" maxCurvedCharAngleIn="25" placementFlags="10" overrunDistanceUnit="MM" geometryGeneratorType="PointGeometry" distUnits="MM" geometryGenerator="" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" placement="0" maxCurvedCharAngleOut="-25"/>
          <rendering minFeatureSize="0" fontLimitPixelSize="0" obstacleType="0" labelPerPart="0" obstacleFactor="1" displayAll="1" limitNumLabels="0" fontMinPixelSize="3" drawLabels="1" maxNumLabels="2000" zIndex="0" upsidedownLabels="0" scaleMin="0" scaleMax="0" mergeLines="0" scaleVisibility="0" obstacle="1" fontMaxPixelSize="10000"/>
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
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot; type=&quot;line&quot; alpha=&quot;1&quot;>&lt;layer locked=&quot;0&quot; enabled=&quot;1&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
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
  <fieldConfiguration>
    <field configurationFlags="None" name="OGC_FID">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="idFeature">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="id">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="numeroParticella">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="subalterno">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="flagConduzione">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option name="map" type="List">
              <Option type="Map">
                <Option name="In conduzione" type="QString" value="S"/>
              </Option>
              <Option type="Map">
                <Option name="Non in conduzione" type="QString" value="N"/>
              </Option>
            </Option>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="flagSospensioneOrig">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="descrizioneSospensione">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="flagLavorato">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="flagCessato">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="flagSospensione">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option name="map" type="List">
              <Option type="Map">
                <Option name="Non sospesa" type="QString" value="0"/>
              </Option>
              <Option type="Map">
                <Option name="Sospesa" type="QString" value="1"/>
              </Option>
            </Option>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="_flagInvalido">
      <editWidget type="Hidden">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" index="0" field="OGC_FID"/>
    <alias name="" index="1" field="idFeature"/>
    <alias name="" index="2" field="id"/>
    <alias name="" index="3" field="numeroParticella"/>
    <alias name="" index="4" field="subalterno"/>
    <alias name="" index="5" field="flagConduzione"/>
    <alias name="" index="6" field="flagSospensioneOrig"/>
    <alias name="" index="7" field="descrizioneSospensione"/>
    <alias name="" index="8" field="flagLavorato"/>
    <alias name="" index="9" field="flagCessato"/>
    <alias name="" index="10" field="flagSospensione"/>
    <alias name="" index="11" field="_flagInvalido"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="OGC_FID" expression=""/>
    <default applyOnUpdate="0" field="idFeature" expression=""/>
    <default applyOnUpdate="0" field="id" expression=""/>
    <default applyOnUpdate="1" field="numeroParticella" expression=" agri_format_numero_particella( &quot;numeroParticella&quot;, 5 )"/>
    <default applyOnUpdate="0" field="subalterno" expression=""/>
    <default applyOnUpdate="0" field="flagConduzione" expression=""/>
    <default applyOnUpdate="0" field="flagSospensioneOrig" expression=""/>
    <default applyOnUpdate="0" field="descrizioneSospensione" expression=""/>
    <default applyOnUpdate="0" field="flagLavorato" expression=""/>
    <default applyOnUpdate="0" field="flagCessato" expression=""/>
    <default applyOnUpdate="0" field="flagSospensione" expression=""/>
    <default applyOnUpdate="0" field="_flagInvalido" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" unique_strength="1" exp_strength="0" field="OGC_FID" notnull_strength="1"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" field="idFeature" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" field="id" notnull_strength="0"/>
    <constraint constraints="4" unique_strength="0" exp_strength="1" field="numeroParticella" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" field="subalterno" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" field="flagConduzione" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" field="flagSospensioneOrig" notnull_strength="0"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" field="descrizioneSospensione" notnull_strength="0"/>
    <constraint constraints="1" unique_strength="0" exp_strength="0" field="flagLavorato" notnull_strength="1"/>
    <constraint constraints="1" unique_strength="0" exp_strength="0" field="flagCessato" notnull_strength="1"/>
    <constraint constraints="1" unique_strength="0" exp_strength="0" field="flagSospensione" notnull_strength="1"/>
    <constraint constraints="1" unique_strength="0" exp_strength="0" field="_flagInvalido" notnull_strength="1"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="OGC_FID"/>
    <constraint exp="" desc="" field="idFeature"/>
    <constraint exp="" desc="" field="id"/>
    <constraint exp=" trim( coalesce(  &quot;numeroParticella&quot;, '' ) ) != ''" desc="" field="numeroParticella"/>
    <constraint exp="" desc="" field="subalterno"/>
    <constraint exp="" desc="" field="flagConduzione"/>
    <constraint exp="" desc="" field="flagSospensioneOrig"/>
    <constraint exp="" desc="" field="descrizioneSospensione"/>
    <constraint exp="" desc="" field="flagLavorato"/>
    <constraint exp="" desc="" field="flagCessato"/>
    <constraint exp="" desc="" field="flagSospensione"/>
    <constraint exp="" desc="" field="_flagInvalido"/>
  </constraintExpressions>
  <expressionfields/>
  <editform tolerant="1"></editform>
  <editforminit>activateFeatureForm</editforminit>
  <editforminitcodesource>2</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
I moduli QGIS possono avere una funzione Python che può essere chiamata quando viene aperto un modulo.

Usa questa funzione per aggiungere logica extra ai tuoi moduli.

Inserisci il nome della funzione nel campo "Funzione Python di avvio".

Segue un esempio:
"""
from qgis.PyQt.QtWidgets import QWidget, QLineEdit
from qgis.PyQt.QtCore import QTimer

def activateFeatureForm(dialog, layer, feature):
    def activate():
        dialog.activateWindow()
        w = dialog.findChild(QLineEdit, "numeroParticella")
        if w:
            w.setFocus()
            w.selectAll()
    QTimer.singleShot( 200, activate ) 
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="OGC_FID" editable="0"/>
    <field name="_flagInvalido" editable="1"/>
    <field name="descrizioneSospensione" editable="1"/>
    <field name="flagCessato" editable="1"/>
    <field name="flagConduzione" editable="1"/>
    <field name="flagLavorato" editable="1"/>
    <field name="flagSospensione" editable="1"/>
    <field name="flagSospensioneOrig" editable="0"/>
    <field name="id" editable="0"/>
    <field name="idFeature" editable="0"/>
    <field name="numeroParticella" editable="1"/>
    <field name="subalterno" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="OGC_FID" labelOnTop="0"/>
    <field name="_flagInvalido" labelOnTop="0"/>
    <field name="descrizioneSospensione" labelOnTop="0"/>
    <field name="flagCessato" labelOnTop="0"/>
    <field name="flagConduzione" labelOnTop="0"/>
    <field name="flagLavorato" labelOnTop="0"/>
    <field name="flagSospensione" labelOnTop="0"/>
    <field name="flagSospensioneOrig" labelOnTop="0"/>
    <field name="id" labelOnTop="0"/>
    <field name="idFeature" labelOnTop="0"/>
    <field name="numeroParticella" labelOnTop="0"/>
    <field name="subalterno" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <layerGeometryType>2</layerGeometryType>
</qgis>
