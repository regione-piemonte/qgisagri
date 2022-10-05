<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology|Labeling" labelsEnabled="0" version="3.16.7-Hannover">
  <renderer-v2 type="RuleRenderer" enableorderby="0" symbollevels="0" forceraster="0">
    <rules key="{7a6ae6c8-81c2-4eda-875b-f7f525cff6c8}">
      <rule symbol="0" label="Foto con direzione - espansa" filter="&quot;direzione&quot; IS NOT NULL AND @map_scale &lt;= 3000" key="{4ebea4c3-daec-45ec-add4-22cb459c2a15}"/>
      <rule symbol="1" label="Foto con direzione - collassata" filter="&quot;direzione&quot; IS NOT NULL AND @map_scale > 3000" key="{b4b4df4f-add3-485a-9bf4-09199215bf72}"/>
      <rule symbol="2" label="Foto generale" filter="ELSE" key="{0abcb6cf-0543-4df9-94ea-27284d9a23b5}"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" name="0" clip_to_extent="1" alpha="1" type="marker">
        <layer locked="0" class="SimpleMarker" enabled="1" pass="0">
          <prop v="0" k="angle"/>
          <prop v="255,0,0,255" k="color"/>
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
          <prop v="1.4" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="angle" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="-180 + (&quot;direzione&quot; + 180)" name="expression" type="QString"/>
                  <Option value="3" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" class="SvgMarker" enabled="1" pass="0">
          <prop v="180" k="angle"/>
          <prop v="255,0,0,159" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="base64:PHN2ZyBlbmFibGUtYmFja2dyb3VuZD0ibmV3IDAgMCAxNjguMjkyIDI4MS4xMjkiIGhlaWdodD0iMjgxLjEyOSIgdmlld0JveD0iMCAwIDE2OC4yOTIgMjgxLjEyOSIgd2lkdGg9IjE2OC4yOTIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgPg0KDQo8cGF0aCBkPSJNODUuMzQ1LDE0LjU2NWMtNDEuODMzLDAtNzUuNzQ2LDMzLjkxMi03NS43NDYsNzUuNzQ1YzAsNjMuMjU0LDc1LjQ3NywxNzUuNzY2LDc1Ljc0NiwxNzUuNzU2ICBjMC4zMjItMC4wMTIsNzUuNzQ2LTExMy41MDIsNzUuNzQ2LTE3NS43NTZDMTYxLjA5MSw0OC40NzcsMTI3LjE4LDE0LjU2NSw4NS4zNDUsMTQuNTY1eiBNODUuNzM4LDE1My41MzggIGMtMzQuOTkxLDAtNjMuMzU2LTI4LjM2NC02My4zNTYtNjMuMzU0UzUwLjc0NywyNi44Myw4NS43MzgsMjYuODNjMzQuOTksMCw2My4zNTQsMjguMzY0LDYzLjM1NCw2My4zNTQgIEMxNDkuMDkxLDEyNS4xNzMsMTIwLjcyOCwxNTMuNTM4LDg1LjczOCwxNTMuNTM4eiIgZmlsbD0icGFyYW0oZmlsbCkiIGZpbGwtb3BhY2l0eT0icGFyYW0oZmlsbC1vcGFjaXR5KSIgc3Ryb2tlPSJwYXJhbShvdXRsaW5lKSIgc3Ryb2tlLW9wYWNpdHk9InBhcmFtKG91dGxpbmUtb3BhY2l0eSkiIHN0cm9rZS13aWR0aD0icGFyYW0ob3V0bGluZS13aWR0aCkiLz4NCg0KPHBhdGggZD0iTTExNy44OTgsNTkuNzA4aC0xMi4xOTZ2LTIuNjAzYzAtNC4zMTItMS43NDctNy44MDctMy45MDItNy44MDdoLTMyLjJjLTIuMTU0LDAtMy45MDIsMy40OTQtMy45MDIsNy44MDd2Mi42MDNINTMuNDk4ICBjLTQuMzExLDAtNy44MDYsMy40OTUtNy44MDYsNy44MDZsLTAuMDAxLDQyLjYxMmMwLDQuMzA5LDMuNDk1LDcuODA2LDcuODA2LDcuODA2aDY0LjRjNC4zMTEsMCw3LjgwNi0zLjQ5Nyw3LjgwNi03LjgwNiAgbDAuMDAyLTQyLjYxMkMxMjUuNzA1LDYzLjIwMywxMjIuMjA4LDU5LjcwOCwxMTcuODk4LDU5LjcwOHogTTg1LjUzNywxMDYuMjIzYy05LjQzMSwwLTE3LjA3Ni03LjY0Ni0xNy4wNzYtMTcuMDc3ICBjMC4wMDEtOS40MzIsNy42NDYtMTcuMDc3LDE3LjA3Ni0xNy4wNzdjOS40MzEsMCwxNy4wNzUsNy42NDYsMTcuMDc0LDE3LjA3N0MxMDIuNjExLDk4LjU3OSw5NC45NjYsMTA2LjIyMyw4NS41MzcsMTA2LjIyM3oiIGZpbGw9InBhcmFtKGZpbGwpIiBmaWxsLW9wYWNpdHk9InBhcmFtKGZpbGwtb3BhY2l0eSkiIHN0cm9rZT0icGFyYW0ob3V0bGluZSkiIHN0cm9rZS1vcGFjaXR5PSJwYXJhbShvdXRsaW5lLW9wYWNpdHkpIiBzdHJva2Utd2lkdGg9InBhcmFtKG91dGxpbmUtd2lkdGgpIi8+DQoNCjwvc3ZnPg==" k="name"/>
          <prop v="0,-6" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,158" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="8" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="angle" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="&quot;direzione&quot; + 180" name="expression" type="QString"/>
                  <Option value="3" name="type" type="int"/>
                </Option>
                <Option name="enabled" type="Map">
                  <Option value="false" name="active" type="bool"/>
                  <Option value="1" name="type" type="int"/>
                  <Option value="" name="val" type="QString"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" name="1" clip_to_extent="1" alpha="0.8" type="marker">
        <layer locked="0" class="SvgMarker" enabled="1" pass="0">
          <prop v="0" k="angle"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="backgrounds/background_circle.svg" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,255,255,255" k="outline_color"/>
          <prop v="0.4" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="7" k="size"/>
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
        <layer locked="0" class="SvgMarker" enabled="1" pass="0">
          <prop v="0" k="angle"/>
          <prop v="253,253,253,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="base64:PHN2ZyBlbmFibGUtYmFja2dyb3VuZD0ibmV3IDAgMCAxNjggMTY4IiBoZWlnaHQ9IjE2OCIgdmlld0JveD0iMCAwIDE2OCAxNjgiIHdpZHRoPSIxNjgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTExNy44OTgsNTkuNzA4aC0xMi4xOTZ2LTIuNjAzYzAtNC4zMTItMS43NDctNy44MDctMy45MDItNy44MDdoLTMyLjJjLTIuMTU0LDAtMy45MDIsMy40OTQtMy45MDIsNy44MDd2Mi42MDNINTMuNDk4ICBjLTQuMzExLDAtNy44MDYsMy40OTUtNy44MDYsNy44MDZsLTAuMDAxLDQyLjYxMmMwLDQuMzA5LDMuNDk1LDcuODA2LDcuODA2LDcuODA2aDY0LjRjNC4zMTEsMCw3LjgwNi0zLjQ5Nyw3LjgwNi03LjgwNiAgbDAuMDAyLTQyLjYxMkMxMjUuNzA1LDYzLjIwMywxMjIuMjA4LDU5LjcwOCwxMTcuODk4LDU5LjcwOHogTTg1LjUzNywxMDYuMjIzYy05LjQzMSwwLTE3LjA3Ni03LjY0Ni0xNy4wNzYtMTcuMDc3ICBjMC4wMDEtOS40MzIsNy42NDYtMTcuMDc3LDE3LjA3Ni0xNy4wNzdjOS40MzEsMCwxNy4wNzUsNy42NDYsMTcuMDc0LDE3LjA3N0MxMDIuNjExLDk4LjU3OSw5NC45NjYsMTA2LjIyMyw4NS41MzcsMTA2LjIyM3oiIGZpbGw9InBhcmFtKGZpbGwpIiBmaWxsLW9wYWNpdHk9InBhcmFtKGZpbGwtb3BhY2l0eSkiIHN0cm9rZT0icGFyYW0ob3V0bGluZSkiIHN0cm9rZS1vcGFjaXR5PSJwYXJhbShvdXRsaW5lLW9wYWNpdHkpIiBzdHJva2Utd2lkdGg9InBhcmFtKG91dGxpbmUtd2lkdGgpIi8+PC9zdmc+" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,255,255,255" k="outline_color"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="8" k="size"/>
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
      <symbol force_rhr="0" name="2" clip_to_extent="1" alpha="0.8" type="marker">
        <layer locked="0" class="SvgMarker" enabled="1" pass="0">
          <prop v="0" k="angle"/>
          <prop v="72,123,182,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="backgrounds/background_circle.svg" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,255,255,255" k="outline_color"/>
          <prop v="0.4" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="7" k="size"/>
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
        <layer locked="0" class="SvgMarker" enabled="1" pass="0">
          <prop v="0" k="angle"/>
          <prop v="253,253,253,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="base64:PHN2ZyBlbmFibGUtYmFja2dyb3VuZD0ibmV3IDAgMCAxNjggMTY4IiBoZWlnaHQ9IjE2OCIgdmlld0JveD0iMCAwIDE2OCAxNjgiIHdpZHRoPSIxNjgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTExNy44OTgsNTkuNzA4aC0xMi4xOTZ2LTIuNjAzYzAtNC4zMTItMS43NDctNy44MDctMy45MDItNy44MDdoLTMyLjJjLTIuMTU0LDAtMy45MDIsMy40OTQtMy45MDIsNy44MDd2Mi42MDNINTMuNDk4ICBjLTQuMzExLDAtNy44MDYsMy40OTUtNy44MDYsNy44MDZsLTAuMDAxLDQyLjYxMmMwLDQuMzA5LDMuNDk1LDcuODA2LDcuODA2LDcuODA2aDY0LjRjNC4zMTEsMCw3LjgwNi0zLjQ5Nyw3LjgwNi03LjgwNiAgbDAuMDAyLTQyLjYxMkMxMjUuNzA1LDYzLjIwMywxMjIuMjA4LDU5LjcwOCwxMTcuODk4LDU5LjcwOHogTTg1LjUzNywxMDYuMjIzYy05LjQzMSwwLTE3LjA3Ni03LjY0Ni0xNy4wNzYtMTcuMDc3ICBjMC4wMDEtOS40MzIsNy42NDYtMTcuMDc3LDE3LjA3Ni0xNy4wNzdjOS40MzEsMCwxNy4wNzUsNy42NDYsMTcuMDc0LDE3LjA3N0MxMDIuNjExLDk4LjU3OSw5NC45NjYsMTA2LjIyMyw4NS41MzcsMTA2LjIyM3oiIGZpbGw9InBhcmFtKGZpbGwpIiBmaWxsLW9wYWNpdHk9InBhcmFtKGZpbGwtb3BhY2l0eSkiIHN0cm9rZT0icGFyYW0ob3V0bGluZSkiIHN0cm9rZS1vcGFjaXR5PSJwYXJhbShvdXRsaW5lLW9wYWNpdHkpIiBzdHJva2Utd2lkdGg9InBhcmFtKG91dGxpbmUtd2lkdGgpIi8+PC9zdmc+" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,255,255,255" k="outline_color"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="8" k="size"/>
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
    </symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>0</layerGeometryType>
</qgis>
