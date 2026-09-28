/* Snow day probability model v2026-09-29.
   Same features as the published back-test (see /methodology/). Pure functions, no DOM. */
(function (root) {
  "use strict";
  var M = {
    intercept: 0, w: [], // filled from coefficients at build time
    TIERS: ["north", "northeast", "midwest", "midatlantic", "south_border", "south"]
  };

  // How used a place is to snow. State-level, with upstate New York treated as "north".
  var STATE_TIER = {
    MN: "north", WI: "north", MI: "north", ND: "north", SD: "north", MT: "north", WY: "north",
    ID: "north", IL: "north", IA: "north", NE: "north", CO: "north", UT: "north", AK: "north",
    ME: "north", VT: "north", NH: "north",
    NY: "northeast", MA: "northeast", CT: "northeast", RI: "northeast", NJ: "northeast", PA: "northeast",
    OH: "midwest", IN: "midwest", MO: "midwest", KS: "midwest",
    MD: "midatlantic", DE: "midatlantic", DC: "midatlantic", VA: "midatlantic", WV: "midatlantic",
    KY: "south_border"
  };
  M.tierFor = function (state, lat) {
    if (state === "NY" && lat >= 42.0) return "north";
    return STATE_TIER[state] || "south";
  };

  function frozen(d, j) {
    if (d.temperature_2m_max[j] <= 34.0) return d.precipitation_sum[j] || 0;
    return (d.snowfall_sum[j] || 0) / 10.0;
  }
  function packSeries(d) {
    var out = [], a = 0;
    for (var j = 0; j < d.time.length; j++) {
      var tmax = d.temperature_2m_max[j];
      var decay = tmax <= 32 ? 1 : Math.exp(-(tmax - 32) / 8.0);
      a = a * decay + frozen(d, j);
      out.push(a);
    }
    return out;
  }
  M.features = function (d, i, pack) {
    pack = pack || packSeries(d);
    var s48 = (d.snowfall_sum[i - 1] || 0) + (d.snowfall_sum[i] || 0);
    var fresh = frozen(d, i - 1) + frozen(d, i);
    var ground = i >= 2 ? pack[i - 2] : 0;
    var wc = d.apparent_temperature_min[i];
    var below = 0;
    for (var j = i - 2; j <= i; j++) if (d.temperature_2m_max[j] <= 32) below++;
    return { s48: s48, fresh: fresh, ground: ground, windChill: wc, cold: Math.max(0, -wc) / 10, below: below };
  };
  M.vector = function (f, tier) {
    var fr = Math.log1p(10 * f.fresh), gr = Math.log1p(10 * f.ground);
    var v = [fr, gr, Math.log1p(f.s48), f.cold, f.below / 3];
    var oh = M.TIERS.map(function (t) { return t === tier ? 1 : 0; });
    return v.concat(oh, oh.map(function (o) { return (fr + gr) * o; }), oh.map(function (o) { return f.cold * o; }));
  };
  M.probability = function (f, tier) {
    var x = M.vector(f, tier), z = M.intercept;
    for (var k = 0; k < x.length; k++) z += M.w[k] * x[k];
    return 1 / (1 + Math.exp(-z));
  };
  // The single biggest reason, in words, for the result card.
  M.driver = function (f) {
    var parts = [];
    if (f.s48 >= 0.5) parts.push(f.s48.toFixed(1) + " in of snow");
    if (f.s48 < 1 && f.fresh >= 0.05) parts.push("freezing rain or sleet");
    if (f.ground >= 0.2) parts.push("snow and ice still on the ground");
    if (f.windChill <= 0) parts.push("wind chill " + Math.round(f.windChill) + "°F");
    if (!parts.length) return "No snow, ice or dangerous cold in the forecast";
    return parts.join(", ").replace(/^./, function (c) { return c.toUpperCase(); });
  };
  M.packSeries = packSeries;
  M.load = function (coef) { M.intercept = coef.intercept; M.w = coef.w; return M; };

  if (typeof module !== "undefined" && module.exports) module.exports = M; else root.SnowModel = M;
})(this);
