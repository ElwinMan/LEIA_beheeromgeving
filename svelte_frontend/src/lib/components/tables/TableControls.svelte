<script lang="ts">
  export let search: string;
  export let onSearch: (value: string) => void;
  export let page: number;
  export let totalPages: number;
  export let pageSize: number;
  export let onPageChange: (p: number) => void;
  export let onPageSizeChange: (size: number) => void;
</script>

<div class="flex justify-between items-center mt-4 p-6 bg-base-200 shadow">
  <div>
    <input
      type="text"
      class="input input-bordered w-full max-w-xs"
      placeholder="Zoek digital twin..."
      bind:value={search}
      oninput={() => onSearch(search)}
    />
  </div>
  <div>
    <div class="join">
      <button class="join-item btn btn-md" onclick={() => onPageChange(page - 1)} disabled={page === 1}>«</button>
      {#if totalPages <= 7}
        {#each Array(totalPages) as _, i}
          <button
            class="join-item btn btn-md {page === i + 1 ? 'btn-active btn-primary' : ''}"
            onclick={() => onPageChange(i + 1)}
          >{i + 1}</button>
        {/each}
      {:else}
        <button
          class="join-item btn btn-md {page === 1 ? 'btn-active btn-primary' : ''}"
          onclick={() => onPageChange(1)}
        >1</button>
        {#if page > 4}
          <button class="join-item btn btn-md btn-disabled">...</button>
        {/if}
        {#each [page - 1, page, page + 1] as p (p)}
          {#if p > 1 && p < totalPages}
            <button
              class="join-item btn btn-md {page === p ? 'btn-active btn-primary' : ''}"
              onclick={() => onPageChange(p)}
            >{p}</button>
          {/if}
        {/each}
        {#if page < totalPages - 3}
          <button class="join-item btn btn-md btn-disabled">...</button>
        {/if}
        <button
          class="join-item btn btn-md {page === totalPages ? 'btn-active btn-primary' : ''}"
          onclick={() => onPageChange(totalPages)}
        >{totalPages}</button>
      {/if}
      <button class="join-item btn btn-md" onclick={() => onPageChange(page + 1)} disabled={page === totalPages}>»</button>
    </div>
  </div>
  <div>
    <select class="select select-mg" bind:value={pageSize} onchange={() => onPageSizeChange(+pageSize)}>
      <option value={10}>10 per pagina</option>
      <option value={20}>20 per pagina</option>
      <option value={50}>50 per pagina</option>
    </select>
  </div>
</div>