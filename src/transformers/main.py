from transformers import pipeline


generation = pipeline('text-generation', model='ibm-granite/granite-4.0-h-350m')
prompt = "Tell me about India"
temperature_value = 0.8
top_p_value = 0.9
max_length_value = 100
output = generation(prompt,max_length=max_length_value,top_p=top_p_value)

print(output[0]['generated_text'])