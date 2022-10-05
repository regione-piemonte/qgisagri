package it.csi.proxy.ogcproxy.pojo;

public class Authorization extends BasePojo {

	private String name;
	private String token;
	private String oneShotToken;
	private long start;
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getToken() {
		return token;
	}
	public void setToken(String token) {
		this.token = token;
	}
	public long getStart() {
		return start;
	}
	public void setStart(long start) {
		this.start = start;
	}
	public String getOneShotToken() {
		return oneShotToken;
	}
	public void setOneShotToken(String oneShotToken) {
		this.oneShotToken = oneShotToken;
	}
	




}