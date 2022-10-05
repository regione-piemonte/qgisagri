package it.csi.proxy.ogcproxy.pojo;

import java.util.HashMap;
import java.util.Map;

public class AuthorizationManager extends BasePojo {

	private static Map<String, Authorization> map = new HashMap<String, Authorization>();
	
	public static AuthorizationManager theInstance = new AuthorizationManager();
	
	public static Map<String, Authorization> getMap() {
		return map;
	}
	
	public static void setMap(Map<String, Authorization> map) {
		AuthorizationManager.map = map;
	}




}