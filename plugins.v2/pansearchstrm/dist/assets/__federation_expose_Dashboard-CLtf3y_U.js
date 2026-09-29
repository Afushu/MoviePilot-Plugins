import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,withCtx:_withCtx,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,openBlock:_openBlock,createBlock:_createBlock} = await importShared('vue');


const {onMounted,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Dashboard',
  props: {
  api: { type: Object, default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
},
  setup(__props) {

const props = __props;

const status = ref({ sources: [] });

/**
 * 读取插件状态，用于仪表板展示。
 */
async function loadStatus() {
  if (!props.api) return
  try {
    const resp = await props.api.get('plugin/PanSearchStrm/status');
    status.value =
      resp && typeof resp === 'object' && ('sources' in resp || 'success' in resp)
        ? resp
        : resp?.data && typeof resp.data === 'object'
          ? resp.data
          : resp || {};
  } catch (error) {
    status.value = { sources: [] };
  }
}

onMounted(loadStatus);

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");

  return (_openBlock(), _createBlock(_component_v_card, {
    flat: "",
    class: "rounded border"
  }, {
    default: _withCtx(() => [
      _createVNode(_component_v_card_title, { class: "text-caption d-flex align-center px-3 py-2" }, {
        default: _withCtx(() => [
          _createVNode(_component_v_icon, {
            icon: "mdi-cloud-search",
            size: "small",
            class: "mr-2",
            color: "primary"
          }),
          _cache[0] || (_cache[0] = _createElementVNode("span", null, "网盘搜索STRM", -1))
        ]),
        _: 1
      }),
      _createVNode(_component_v_card_text, { class: "px-3 py-2 text-caption" }, {
        default: _withCtx(() => [
          _createTextVNode(" 已启用渠道：" + _toDisplayString((status.value.sources || []).join('、') || '未启用'), 1)
        ]),
        _: 1
      })
    ]),
    _: 1
  }))
}
}

};

export { _sfc_main as default };
