import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _sfc_main$1 } from './SearchPanel-DwIoG6ky.js';

true&&(function polyfill() {
  const relList = document.createElement("link").relList;
  if (relList && relList.supports && relList.supports("modulepreload")) {
    return;
  }
  for (const link of document.querySelectorAll('link[rel="modulepreload"]')) {
    processPreload(link);
  }
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type !== "childList") {
        continue;
      }
      for (const node of mutation.addedNodes) {
        if (node.tagName === "LINK" && node.rel === "modulepreload")
          processPreload(node);
      }
    }
  }).observe(document, { childList: true, subtree: true });
  function getFetchOpts(link) {
    const fetchOpts = {};
    if (link.integrity) fetchOpts.integrity = link.integrity;
    if (link.referrerPolicy) fetchOpts.referrerPolicy = link.referrerPolicy;
    if (link.crossOrigin === "use-credentials")
      fetchOpts.credentials = "include";
    else if (link.crossOrigin === "anonymous") fetchOpts.credentials = "omit";
    else fetchOpts.credentials = "same-origin";
    return fetchOpts;
  }
  function processPreload(link) {
    if (link.ep)
      return;
    link.ep = true;
    const fetchOpts = getFetchOpts(link);
    fetch(link.href, fetchOpts);
  }
}());

const {createVNode:_createVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock} = await importShared('vue');

/**
 * 开发预览用的空实现，正式运行时由 MoviePilot 注入真实 api 对象。
 */

const _sfc_main = {
  __name: 'App',
  setup(__props) {

const mockApi = {
  get: async () => ({ data: {} }),
  post: async () => ({ data: {} }),
};

return (_ctx, _cache) => {
  const _component_v_main = _resolveComponent("v-main");
  const _component_v_app = _resolveComponent("v-app");

  return (_openBlock(), _createBlock(_component_v_app, null, {
    default: _withCtx(() => [
      _createVNode(_component_v_main, { class: "pa-4" }, {
        default: _withCtx(() => [
          _createVNode(_sfc_main$1, {
            api: mockApi,
            "plugin-id": "PanSearchStrm"
          })
        ]),
        _: 1
      })
    ]),
    _: 1
  }))
}
}

};

const {createApp} = await importShared('vue');

createApp(_sfc_main).mount('#app');
