import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,unref:_unref,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };
const _hoisted_2 = { class: "d-flex justify-end" };

const {computed,reactive,ref,watch} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, default: null },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['save', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const error = ref('');
const message = ref('');
const saving = ref(false);

const urlModeItems = [
  { title: '插件跳转端点（播放时 302 到 115 直链）', value: 'redirect' },
  { title: '直接写入 115 分享链接', value: 'share' },
];

/**
 * 生成带默认值的表单模型，确保嵌套字段始终存在。
 */
function buildForm(raw) {
  const source = raw || {};
  return reactive({
    enabled: Boolean(source.enabled),
    notify: source.notify !== false,
    search_inject_enabled: source.search_inject_enabled !== false,
    moviepilot_address: source.moviepilot_address || '',
    pansou: {
      enabled: Boolean(source.pansou?.enabled),
      base_url: source.pansou?.base_url || 'https://pansou.cc',
      username: source.pansou?.username || '',
      password: source.pansou?.password || '',
      result_limit: source.pansou?.result_limit ?? 20,
      timeout: source.pansou?.timeout ?? 30,
    },
    juying: {
      enabled: Boolean(source.juying?.enabled),
      base_url: source.juying?.base_url || 'https://www.jying.top',
      username: source.juying?.username || '',
      password: source.juying?.password || '',
      result_limit: source.juying?.result_limit ?? 20,
      timeout: source.juying?.timeout ?? 30,
    },
    telegram: {
      enabled: Boolean(source.telegram?.enabled),
      api_id: source.telegram?.api_id || '',
      api_hash: source.telegram?.api_hash || '',
      channels: Array.isArray(source.telegram?.channels) ? [...source.telegram.channels] : [],
      search_global: Boolean(source.telegram?.search_global),
      result_limit: source.telegram?.result_limit ?? 20,
      timeout: source.telegram?.timeout ?? 30,
    },
    p115: {
      cookies: source.p115?.cookies || '',
      receive_path: source.p115?.receive_path || '/网盘搜索转存',
      share_duration: source.p115?.share_duration ?? -1,
      auto_renewal: source.p115?.auto_renewal !== false,
      request_timeout: source.p115?.request_timeout ?? 60,
    },
    strm: {
      enabled: source.strm?.enabled !== false,
      output_path: source.strm?.output_path || '/media/网盘/STRM',
      url_mode: source.strm?.url_mode || 'redirect',
      media_ext: source.strm?.media_ext || 'mp4,mkv,ts,iso,m2ts,avi,rmvb,flv,mov,wmv',
      overwrite: Boolean(source.strm?.overwrite),
    },
  })
}

const form = buildForm(props.initialConfig);
const telegramChannels = ref((form.telegram.channels || []).join('\n'));

watch(
  () => props.initialConfig,
  (value) => {
    Object.assign(form, buildForm(value));
    telegramChannels.value = (form.telegram.channels || []).join('\n');
  }
);

/**
 * 提交配置到插件接口。
 */
async function submit() {
  error.value = '';
  message.value = '';
  form.telegram.channels = String(telegramChannels.value || '')
    .split('\n')
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
  if (!props.api) {
    message.value = '开发预览模式：配置未提交';
    return
  }
  saving.value = true;
  try {
    const resp = await props.api.post('plugin/PanSearchStrm/config', form);
    const payload =
      resp && typeof resp === 'object' && 'success' in resp
        ? resp
        : resp?.data && typeof resp.data === 'object'
          ? resp.data
          : resp || {};
    if (payload.success === false) {
      error.value = payload.message || '保存失败';
    } else {
      message.value = '配置已保存';
      emit('save', form);
    }
  } catch (err) {
    error.value = String(err?.message || err);
  } finally {
    saving.value = false;
  }
}

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_v_select = _resolveComponent("v-select");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, {
      flat: "",
      class: "rounded border"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, { class: "text-subtitle-1 d-flex align-center px-3 py-2 bg-primary-lighten-5" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_icon, {
              icon: "mdi-cog",
              class: "mr-2",
              color: "primary",
              size: "small"
            }),
            _cache[30] || (_cache[30] = _createElementVNode("span", null, "网盘搜索STRM 配置", -1)),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              size: "small",
              variant: "text",
              onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('switch')))
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-arrow-left",
                  size: "small",
                  class: "mr-1"
                }),
                _cache[29] || (_cache[29] = _createTextVNode(" 返回 ", -1))
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
          default: _withCtx(() => [
            (error.value)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 0,
                  type: "error",
                  density: "compact",
                  variant: "tonal",
                  class: "mb-2 text-caption",
                  closable: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(error.value), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            (message.value)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 1,
                  type: "success",
                  density: "compact",
                  variant: "tonal",
                  class: "mb-2 text-caption",
                  closable: ""
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(message.value), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            _createVNode(_component_v_card, {
              flat: "",
              class: "rounded border mb-3"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "text-caption px-3 py-2 bg-primary-lighten-5" }, {
                  default: _withCtx(() => [...(_cache[31] || (_cache[31] = [
                    _createTextVNode("基础设置", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).enabled,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((_unref(form).enabled) = $event)),
                      label: "启用插件",
                      color: "primary",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).notify,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((_unref(form).notify) = $event)),
                      label: "操作完成后发送通知",
                      color: "primary",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).search_inject_enabled,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((_unref(form).search_inject_enabled) = $event)),
                      label: "把网盘资源并入默认「搜索资源」结果（搜索 PT 资源时同时返回网盘资源）",
                      color: "primary",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).moviepilot_address,
                      "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((_unref(form).moviepilot_address) = $event)),
                      label: "MoviePilot 访问地址（用于生成 STRM 跳转端点）",
                      placeholder: "http://192.168.1.10:3001",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card, {
              flat: "",
              class: "rounded border mb-3"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "text-caption px-3 py-2 bg-primary-lighten-5" }, {
                  default: _withCtx(() => [...(_cache[32] || (_cache[32] = [
                    _createTextVNode("盘搜渠道", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).pansou.enabled,
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((_unref(form).pansou.enabled) = $event)),
                      label: "启用盘搜",
                      color: "primary",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).pansou.base_url,
                      "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((_unref(form).pansou.base_url) = $event)),
                      label: "盘搜服务地址",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).pansou.username,
                      "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((_unref(form).pansou.username) = $event)),
                      label: "用户名（可选）",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).pansou.password,
                      "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((_unref(form).pansou.password) = $event)),
                      label: "密码（可选）",
                      type: "password",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).pansou.result_limit,
                      "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((_unref(form).pansou.result_limit) = $event)),
                      modelModifiers: { number: true },
                      label: "结果条数上限",
                      type: "number",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card, {
              flat: "",
              class: "rounded border mb-3"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "text-caption px-3 py-2 bg-primary-lighten-5" }, {
                  default: _withCtx(() => [...(_cache[33] || (_cache[33] = [
                    _createTextVNode("聚影渠道", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).juying.enabled,
                      "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((_unref(form).juying.enabled) = $event)),
                      label: "启用聚影",
                      color: "primary",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).juying.base_url,
                      "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((_unref(form).juying.base_url) = $event)),
                      label: "聚影站点地址",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).juying.username,
                      "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((_unref(form).juying.username) = $event)),
                      label: "账号",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).juying.password,
                      "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((_unref(form).juying.password) = $event)),
                      label: "密码",
                      type: "password",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).juying.result_limit,
                      "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((_unref(form).juying.result_limit) = $event)),
                      modelModifiers: { number: true },
                      label: "结果条数上限",
                      type: "number",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card, {
              flat: "",
              class: "rounded border mb-3"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "text-caption px-3 py-2 bg-primary-lighten-5" }, {
                  default: _withCtx(() => [...(_cache[34] || (_cache[34] = [
                    _createTextVNode("Telegram 渠道（扫码授权）", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).telegram.enabled,
                      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((_unref(form).telegram.enabled) = $event)),
                      label: "启用 Telegram",
                      color: "primary",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).telegram.api_id,
                      "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((_unref(form).telegram.api_id) = $event)),
                      label: "api_id（my.telegram.org 申请）",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).telegram.api_hash,
                      "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((_unref(form).telegram.api_hash) = $event)),
                      label: "api_hash",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_textarea, {
                      modelValue: telegramChannels.value,
                      "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((telegramChannels).value = $event)),
                      label: "搜索频道（每行一个，如 pan115share）",
                      variant: "outlined",
                      density: "compact",
                      rows: "4",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).telegram.search_global,
                      "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((_unref(form).telegram.search_global) = $event)),
                      label: "额外做账号全局搜索",
                      color: "primary",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card, {
              flat: "",
              class: "rounded border mb-3"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "text-caption px-3 py-2 bg-primary-lighten-5" }, {
                  default: _withCtx(() => [...(_cache[35] || (_cache[35] = [
                    _createTextVNode("115 网盘", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).p115.receive_path,
                      "onUpdate:modelValue": _cache[20] || (_cache[20] = $event => ((_unref(form).p115.receive_path) = $event)),
                      label: "转存目标目录",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).p115.share_duration,
                      "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((_unref(form).p115.share_duration) = $event)),
                      modelModifiers: { number: true },
                      label: "分享有效期天数（-1 为长期）",
                      type: "number",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).p115.auto_renewal,
                      "onUpdate:modelValue": _cache[22] || (_cache[22] = $event => ((_unref(form).p115.auto_renewal) = $event)),
                      label: "开启分享自动续期",
                      color: "primary",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).p115.request_timeout,
                      "onUpdate:modelValue": _cache[23] || (_cache[23] = $event => ((_unref(form).p115.request_timeout) = $event)),
                      modelModifiers: { number: true },
                      label: "请求超时（秒）",
                      type: "number",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card, {
              flat: "",
              class: "rounded border mb-3"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "text-caption px-3 py-2 bg-primary-lighten-5" }, {
                  default: _withCtx(() => [...(_cache[36] || (_cache[36] = [
                    _createTextVNode("STRM 生成", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "px-3 py-2" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).strm.enabled,
                      "onUpdate:modelValue": _cache[24] || (_cache[24] = $event => ((_unref(form).strm.enabled) = $event)),
                      label: "生成 STRM",
                      color: "primary",
                      density: "compact",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).strm.output_path,
                      "onUpdate:modelValue": _cache[25] || (_cache[25] = $event => ((_unref(form).strm.output_path) = $event)),
                      label: "STRM 输出目录",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_select, {
                      modelValue: _unref(form).strm.url_mode,
                      "onUpdate:modelValue": _cache[26] || (_cache[26] = $event => ((_unref(form).strm.url_mode) = $event)),
                      items: urlModeItems,
                      "item-title": "title",
                      "item-value": "value",
                      label: "STRM 内容模式",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: _unref(form).strm.media_ext,
                      "onUpdate:modelValue": _cache[27] || (_cache[27] = $event => ((_unref(form).strm.media_ext) = $event)),
                      label: "媒体扩展名（逗号分隔）",
                      variant: "outlined",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_v_switch, {
                      modelValue: _unref(form).strm.overwrite,
                      "onUpdate:modelValue": _cache[28] || (_cache[28] = $event => ((_unref(form).strm.overwrite) = $event)),
                      label: "覆盖已存在的 STRM",
                      color: "primary",
                      density: "compact",
                      "hide-details": "",
                      class: "mt-2"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createElementVNode("div", _hoisted_2, [
              _createVNode(_component_v_btn, {
                color: "primary",
                variant: "flat",
                loading: saving.value,
                onClick: submit
              }, {
                default: _withCtx(() => [...(_cache[37] || (_cache[37] = [
                  _createTextVNode("保存配置", -1)
                ]))]),
                _: 1
              }, 8, ["loading"])
            ])
          ]),
          _: 1
        })
      ]),
      _: 1
    })
  ]))
}
}

};

export { _sfc_main as default };
