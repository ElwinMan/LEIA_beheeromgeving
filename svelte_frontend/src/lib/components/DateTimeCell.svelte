<script lang="ts">
  export let value: string | null;

  function formatLocalDateTime(utcString: string | null): string {
    if (!utcString) return '-';
    const date = new Date(utcString);
    return date.toLocaleString();
  }
</script>

<span>{formatLocalDateTime(value)}</span>
