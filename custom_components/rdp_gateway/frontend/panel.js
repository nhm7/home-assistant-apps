class RdpGatewayPanel extends HTMLElement {
  set hass(hass) { this._hass = hass; this.open(); }
  async open() {
    if (this._opened || !this._hass) return;
    this._opened = true;
    const result = await this._hass.callWS({type: "rdp_gateway/create_session"});
    const frame = document.createElement("iframe");
    frame.src = result.url; frame.style.cssText = "border:0;width:100%;height:100%;position:absolute";
    this.append(frame);
  }
}
customElements.define("rdp-gateway-panel", RdpGatewayPanel);
