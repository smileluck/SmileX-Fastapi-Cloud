import { computed, ref, toValue, watch, type Ref } from 'vue';
import { fetchGetDictItemsByDictCode } from '@/service/api/system-manage';

interface DictCacheEntry {
  data: Api.SystemManage.DictItem[];
  promise: Promise<Api.SystemManage.DictItem[]> | null;
  loaded: boolean;
}

const dictCache = new Map<string, DictCacheEntry>();

function loadDictItems(code: string): Promise<Api.SystemManage.DictItem[]> {
  const cached = dictCache.get(code);
  if (cached?.loaded) return Promise.resolve(cached.data);
  if (cached?.promise) return cached.promise;

  const promise = fetchGetDictItemsByDictCode(code).then(({ data, error }) => {
    const entry = dictCache.get(code)!;
    if (!error && data) {
      entry.data = data;
      entry.loaded = true;
    } else {
      entry.promise = null;
    }
    return entry.data;
  });

  if (!dictCache.has(code)) {
    dictCache.set(code, { data: [], promise: null, loaded: false });
  }
  dictCache.get(code)!.promise = promise;

  return promise;
}

export function useDict(code: string | Ref<string> | (() => string)) {
  const loading = ref(false);
  const items = ref<Api.SystemManage.DictItem[]>([]) as Ref<Api.SystemManage.DictItem[]>;

  const options = computed(() => items.value.map(item => ({ label: item.label, value: item.value })));

  function getLabelByValue(value: string | null | undefined): string {
    if (value == null) return '';
    const found = items.value.find(item => item.value === value);
    return found ? found.label : value;
  }

  async function load() {
    const codeValue = toValue(code);
    if (!codeValue) return;

    const cached = dictCache.get(codeValue);
    if (cached?.loaded) {
      items.value = cached.data;
      return;
    }

    loading.value = true;
    try {
      const data = await loadDictItems(codeValue);
      items.value = data;
    } finally {
      loading.value = false;
    }
  }

  async function refresh() {
    const codeValue = toValue(code);
    if (!codeValue) return;
    dictCache.delete(codeValue);
    await load();
  }

  watch(() => toValue(code), load, { immediate: true });

  return { items, options, loading, getLabelByValue, refresh };
}
