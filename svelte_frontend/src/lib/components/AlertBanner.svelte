<script lang="ts">
  export let type: 'success' | 'error' | 'info' = 'info';
  export let message = '';
  export let duration = 4000;

  let visible = false;

  export function show() {
    visible = true;
    setTimeout(() => {
      visible = false;
    }, duration);
  }
</script>

{#if visible}
  <div
    role="alert"
    aria-live="assertive"
    class={`fixed top-4 left-1/2 z-50 flex -translate-x-1/2 transform items-center space-x-2 rounded px-4 py-3
      ${type === 'success' ? 'bg-green-100 text-green-800' : ''}
      ${type === 'error' ? 'bg-red-100 text-red-800' : ''}
      ${type === 'info' ? 'bg-blue-100 text-blue-800' : ''}
    `}
  >
    {#if type === 'success'}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
        stroke-linecap="round"
        stroke-linejoin="round"><path d="M9 12l2 2 4-4" /></svg
      >
    {:else if type === 'error'}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
        stroke-linecap="round"
        stroke-linejoin="round"
        ><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line
          x1="9"
          y1="9"
          x2="15"
          y2="15"
        /></svg
      >
    {:else}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
        stroke-linecap="round"
        stroke-linejoin="round"
        ><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><circle
          cx="12"
          cy="16"
          r="1"
        /></svg
      >
    {/if}
    <span>{message}</span>
  </div>
{/if}
