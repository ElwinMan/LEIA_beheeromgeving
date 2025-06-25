<script>
  export let data;
</script>

<h1>Digital Twins</h1>
<ul>
  {#each data.digitalTwins as twin}
    <li>Name: {twin.name}</li>
    <li>Title: {twin.title}</li>
    <li>Subtitle: {twin.subtitle}</li>
    <br>
  {/each}
</ul>
