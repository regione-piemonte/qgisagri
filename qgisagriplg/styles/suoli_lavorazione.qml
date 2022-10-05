<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="1" version="3.16.16-Hannover" styleCategories="Symbology|Labeling">
  <renderer-v2 forceraster="0" symbollevels="0" enableorderby="0" type="RuleRenderer">
    <rules key="{4471d421-25eb-4cbd-85fd-ad3b6f64fb81}">
      <rule filter="&quot;tipoSuolo&quot; IN ('LAV', 'LAV_KO')" key="{fd593514-18fd-4b1c-90b5-82a41db3bf3b}" label="Suoli lavorazione" symbol="0">
        <rule filter="&quot;tipoSuolo&quot; = 'LAV'" key="{c6fc96e1-8952-4c6a-bf2e-5cfe1ce8de34}" label="Ok" symbol="1">
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; = 1" key="{800ae0b1-4164-4c47-92f8-27e009465924}" label="Sospesi" symbol="2"/>
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; != 1" key="{e59ef491-bd7e-447b-8656-9af86da4a9da}" label="Lavorati" symbol="3"/>
        </rule>
        <rule filter="&quot;tipoSuolo&quot; = 'LAV_KO'" key="{4ef36201-8327-4486-b8bd-97692af71bc9}" label="Corrotti" symbol="4">
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; = 1" key="{4d241abf-c7a3-4d64-8d52-48dcae755691}" label="Sospesi" symbol="5"/>
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; != 1" key="{32fabc27-9b77-48d1-b67e-2515eaeae714}" label="Lavorati" symbol="6"/>
        </rule>
      </rule>
      <rule filter="&quot;tipoSuolo&quot; IN ('COND', 'COND_KO')" key="{d16b1e42-d128-495f-a8de-635a123ff656}" label="Suoli no lavorazione" symbol="7">
        <rule filter="&quot;tipoSuolo&quot; = 'COND'" key="{b8f2777c-7c24-4c70-ac9c-484e3bb62f85}" label="Ok" symbol="8">
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; = 1" key="{9aa50ca8-53e9-451f-9d94-fa9f24620ee4}" label="Sospesi" symbol="9"/>
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; != 1" key="{3c4c058c-c7ae-48ce-9170-8b1413d5efef}" label="Modificati" symbol="10"/>
        </rule>
        <rule filter="&quot;tipoSuolo&quot; = 'COND_KO'" key="{896d4721-16d3-4029-a937-c61fbc300733}" label="Corrotti" symbol="11">
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; = 1" key="{73ee7295-7162-4d69-9bf2-1076d40142d8}" label="Sospesi" symbol="12"/>
          <rule filter="&quot;flagLavorato&quot; = 1 AND  &quot;flagSospensione&quot; != 1" key="{6ff04c02-a4cf-4f37-b731-d24072d2967d}" label="Modificati" symbol="13"/>
        </rule>
      </rule>
      <rule filter=" &quot;flagControlloCampo&quot; = 'S'" checkstate="0" key="{8b811044-7180-4b8e-85b4-801806c9d9f0}" label="Controllato in campo" symbol="14"/>
      <rule filter=" &quot;flagSospensione&quot; = 1" checkstate="0" key="{bf404674-140e-46e1-9e3f-c23315a564b3}" label="Sospeso" symbol="15"/>
      <rule filter=" &quot;_flagInvalido&quot;  = 1" key="{3c5d7e64-6fe1-4b17-a25d-2b0b52f9e53b}" label="Invalido" symbol="16"/>
      <rule checkstate="0" key="{cc311d23-8bea-4ac3-9bc7-906cc08b954c}" label="Evidenzia vertici" symbol="17"/>
    </rules>
    <symbols>
      <symbol name="0" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,66,3,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,0" k="outline_color"/>
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
      <symbol name="1" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="252,49,34,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="252,49,34,255" k="outline_color"/>
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
          <prop v="252,49,34,255" k="color"/>
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
      <symbol name="10" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
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
      <symbol name="11" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="250,13,243,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="250,13,243,255" k="outline_color"/>
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
          <prop v="250,13,243,255" k="color"/>
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
      <symbol name="12" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="237,243,44,255" k="color"/>
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
      <symbol name="13" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="251,34,34,255" k="color"/>
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
      <symbol name="14" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
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
          <prop v="0" k="use_custom_dash"/>
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
      <symbol name="15" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="SimpleLine" enabled="1" pass="20" locked="0">
          <prop v="0" k="align_dash_pattern"/>
          <prop v="square" k="capstyle"/>
          <prop v="5;2" k="customdash"/>
          <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
          <prop v="MM" k="customdash_unit"/>
          <prop v="0" k="dash_pattern_offset"/>
          <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
          <prop v="MM" k="dash_pattern_offset_unit"/>
          <prop v="0" k="draw_inside_polygon"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="251,219,9,255" k="line_color"/>
          <prop v="dot" k="line_style"/>
          <prop v="1.96" k="line_width"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0" k="ring_filter"/>
          <prop v="0" k="tweak_dash_pattern_on_corners"/>
          <prop v="0" k="use_custom_dash"/>
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
      <symbol name="16" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="CentroidFill" enabled="1" pass="30" locked="0">
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
          <symbol name="@16@0" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
            <layer class="SimpleMarker" enabled="1" pass="0" locked="0">
              <prop v="0" k="angle"/>
              <prop v="228,0,35,255" k="color"/>
              <prop v="1" k="horizontal_anchor_point"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="equilateral_triangle" k="name"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="255,255,255,255" k="outline_color"/>
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
      <symbol name="17" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="MarkerLine" enabled="1" pass="40" locked="0">
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
          <symbol name="@17@0" clip_to_extent="1" force_rhr="0" type="marker" alpha="1">
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
      <symbol name="2" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="237,243,44,255" k="color"/>
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
      <symbol name="3" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="73,44,243,255" k="color"/>
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
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="249,9,229,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="249,9,229,255" k="outline_color"/>
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
          <prop v="249,9,229,255" k="color"/>
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
      <symbol name="5" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="237,243,44,255" k="color"/>
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
      <symbol name="6" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="250,42,19,255" k="color"/>
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
      <symbol name="7" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="183,72,75,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,0" k="outline_color"/>
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
      <symbol name="8" clip_to_extent="1" force_rhr="0" type="fill" alpha="1">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="9,232,38,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="9,232,38,255" k="outline_color"/>
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
          <prop v="9,232,38,255" k="color"/>
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
      <symbol name="9" clip_to_extent="1" force_rhr="0" type="fill" alpha="0.5">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="237,243,44,255" k="color"/>
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
    </symbols>
  </renderer-v2>
  <labeling type="rule-based">
    <rules key="{6a88ce17-33f2-40c3-b2d0-a418f46c7ffd}">
      <rule scalemindenom="1" description="Eleggibilità" key="{d3f8d79e-ed87-49e2-905b-658a685eb5cc}" scalemaxdenom="100000">
        <settings calloutType="simple">
          <text-style fontFamily="MS Shell Dlg 2" blendMode="0" fieldName="codiceEleggibilitaRilevata" previewBkgrdColor="255,255,255,255" namedStyle="Normale" textOpacity="1" fontItalic="0" textOrientation="horizontal" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSize="10" textColor="0,0,0,255" fontLetterSpacing="0" fontWeight="50" allowHtml="0" fontStrikeout="0" fontWordSpacing="0" fontKerning="1" fontSizeUnit="Point" fontUnderline="0" isExpression="0" capitalization="0" useSubstitutions="0" multilineHeight="1">
            <text-buffer bufferBlendMode="0" bufferSizeUnits="MM" bufferColor="251,34,34,255" bufferOpacity="0.313" bufferDraw="1" bufferJoinStyle="128" bufferSize="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="1">
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
            <background shapeOffsetY="0" shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeBorderWidth="0" shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="250,44,44,255" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeSizeType="0" shapeBorderColor="128,128,128,255" shapeBorderWidthUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeDraw="1" shapeSizeX="0" shapeRotation="0" shapeRadiiY="0" shapeJoinStyle="64" shapeType="0" shapeRotationType="0" shapeBlendMode="0" shapeSizeY="0" shapeOffsetX="0">
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
      <rule scalemindenom="1" description="Note richiesta" key="{c274ce80-cc44-43d6-b5d0-f804e9f5a41d}" scalemaxdenom="100000">
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
      <rule scalemindenom="1" description="Note lavorazione" key="{d73f7681-2c44-4732-b5ef-3500444c6219}" scalemaxdenom="100000">
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
      <rule scalemindenom="1" description="Descrizione sospensione" key="{c9504f88-82e6-4c6b-bf45-43b40b98d0c9}" scalemaxdenom="100000">
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
      <rule active="0" scalemindenom="1" description="Area" key="{caa3a3d6-5e81-49f5-b887-b775d17e6627}" scalemaxdenom="3000">
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
