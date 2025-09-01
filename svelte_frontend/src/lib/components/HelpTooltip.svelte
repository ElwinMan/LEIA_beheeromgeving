<script lang="ts">
  export let tip: string = '';
  export let position: 'top' | 'right' | 'bottom' | 'left' = 'top';
  
  $: tooltipClass = {
    top: 'tooltip-top',
    right: 'tooltip-right', 
    bottom: 'tooltip-bottom',
    left: 'tooltip-left'
  }[position];
</script>

<div class="tooltip {tooltipClass}" data-tip={tip}>
  <div class="flex items-center justify-center w-4 h-4 rounded-full bg-base-300 text-base-content text-xs cursor-help">
    ?
  </div>
</div>
