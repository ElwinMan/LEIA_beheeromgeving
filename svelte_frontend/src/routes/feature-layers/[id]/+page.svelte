<script>
  export let data;
  const { layer } = data;
</script>

<h1>{layer.title}</h1>
<p>Type: {layer.type}</p>
<p>Url: {layer.url}</p>
<p>FeatureName: {layer.featureName}</p>
<p>isbackground: {layer.isBackground ? 'true' : 'false'}</p>
