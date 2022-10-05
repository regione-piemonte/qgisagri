package it.csi.qgisagri.agriapi.util.conversion;

import java.util.Map;
import java.util.Map.Entry;

public class FeatureTypeHandler {
  
  private Object[] attributes;

  public FeatureTypeHandler(Map<String, Object> attributesMap) {
    this.attributes = createAttributeArray(attributesMap);
  }

  private Object[] createAttributeArray(Map<String, Object> attributesMap) {
    this.attributes = new Object[attributesMap.size()];
    int i=0;
    for (Entry<String, Object> entry : attributesMap.entrySet()) {
      this.attributes[i++] = entry;
    }
    return this.attributes;
  }
  
  /**
   * Returns a coherently ordered attributes list
   * @return an ordered attributes array
   */
  public Object[] getOrderedAttributeList() {
    return this.attributes;
  }
}

