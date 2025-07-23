<script lang="ts">
  export let column: string;
  export let label: string;
  export let sortColumn: string;
  export let sortDirection: 'asc' | 'desc';
  export let setSort: (column: string) => void;
  export let className: string = "bg-base-200 font-bold cursor-pointer";
</script>

<th class={className} onclick={() => setSort(column)}>
  {label}
  {#if sortColumn === column}
    {#if sortDirection === 'asc'}
      <img src="/icons/chevron-up.svg" alt="Sorteren oplopend" class="inline w-4 h-4" />
    {:else}
      <img src="/icons/chevron-down.svg" alt="Sorteren aflopend" class="inline w-4 h-4" />
    {/if}
  {:else}
    <img src="/icons/chevrons-up-down.svg" alt="Niet gesorteerd" class="inline w-4 h-4 opacity-50" />
  {/if}
</th>