<script>
	export let data;
</script>

<h1>Layers</h1>
<ul>
  {#each data.layers as layer}
    <li>Title: {layer.title}</li>
    <li>Type: {layer.type}</li>
    <li>Url: {layer.url}</li>
    <li>FeatureName: {layer.featureName}</li>
    <li>isbackground: {layer.isbackground ? 'true' : 'false'}</li>
    <br>
  {/each}
</ul>
