import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _sfc_main$1 } from './SearchPanel-DwIoG6ky.js';

const {createVNode:_createVNode,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "pansearch-app-page" };


const _sfc_main = {
  __name: 'AppPage',
  props: {
  api: { type: Object, default: null },
  pluginId: { type: String, default: 'PanSearchStrm' },
  navKey: { type: String, default: 'main' },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_sfc_main$1, {
      api: __props.api,
      "plugin-id": __props.pluginId,
      "nav-key": __props.navKey
    }, null, 8, ["api", "plugin-id", "nav-key"])
  ]))
}
}

};

export { _sfc_main as default };
