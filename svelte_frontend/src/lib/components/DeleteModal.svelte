<script lang="ts">

  interface Props {
    show?: boolean;
    title?: string;
    message?: string;
    confirmLabel?: string;
    cancelLabel?: string;
    showCheckbox?: boolean;
    checkboxLabel?: string;
    onconfirm?: (detail: { doNotAskAgain: boolean }) => void;
    oncancel?: () => void;
  }

  let {
    show = false,
    title = '',
    message = '',
    confirmLabel = 'Verwijder',
    cancelLabel = 'Annuleer',
    showCheckbox = false,
    checkboxLabel = 'Niet meer vragen',
    onconfirm,
    oncancel
  }: Props = $props();

  let checkboxValue = $state(false);

  function handleConfirm() {
    onconfirm?.({ doNotAskAgain: checkboxValue });
    // Reset checkbox for next time
    checkboxValue = false;
  }

  function handleCancel() {
    oncancel?.();
    // Reset checkbox for next time
    checkboxValue = false;
  }

  // Reset checkbox when modal is closed
  $effect(() => {
    if (!show) {
      checkboxValue = false;
    }
  });
</script>

{#if show}
  <div class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
    <div class="bg-base-100 rounded-lg shadow-lg p-6 w-full max-w-md">
      <h2 class="text-lg font-bold mb-2 flex items-center gap-2">
        <img src="/icons/trash-2.svg" alt="Trash" class="w-5 h-5 text-error" />
        {title}
      </h2>
      <p class="mb-4">{message}</p>
      {#if showCheckbox}
        <label class="flex items-center gap-2 mb-4 cursor-pointer">
          <input 
            type="checkbox" 
            class="checkbox checkbox-sm" 
            bind:checked={checkboxValue} 
          />
          <span class="text-sm">{checkboxLabel}</span>
        </label>
      {/if}
      <div class="flex gap-2 justify-end">
        <button class="btn btn-error btn-sm" onclick={handleConfirm}>
          {confirmLabel}
        </button>
        <button class="btn btn-ghost btn-sm" onclick={handleCancel}>
          {cancelLabel}
        </button>
      </div>
    </div>
  </div>
{/if}