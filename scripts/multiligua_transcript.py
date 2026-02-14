from clm_core import CLMEncoder, CLMConfig

map = {
    "es": """Cliente: Hola Raj, noté un cargo extra en mi tarjeta por mi plan este mes. Parece que me facturaron dos veces por la misma suscripción.
            Agente: Lo siento, veamos juntos. ¿Me podrías dar el correo electrónico o el ID de facturación de tu cuenta para verificar tu historial?
            Cliente: Claro, soy melissa.jordan@example.com.
            Agente: Gracias, Melissa. Un momento... Bien, veo dos transacciones en tu archivo: una procesada el día 2 y otra el 3. Parece que el sistema reintentó el pago incluso después de que el primero se procesara correctamente.
            Cliente: Vaya, eso lo explica. Entonces no estoy loco.
            Agente: Para nada. Es un problema conocido que tuvimos a principios de esta semana con el procesamiento duplicado. La buena noticia es que puedes obtener un reembolso completo del segundo cargo.
            Cliente: Genial. ¿Cuánto tardará en aparecer? 
            Agente: Una vez que presento el reembolso, suele reflejarse en un plazo de 3 a 5 días hábiles, dependiendo de su banco. También le enviaré un correo electrónico de confirmación con el número de referencia.
            Cliente: Perfecto. Gracias por solucionarlo tan rápido.
            Agente: Un placer. Acabo de enviar la solicitud de reembolso; su número de referencia es RFD-908712. Debería ver la actualización más tarde.
            Cliente: Perfecto. Agradezco su ayuda, Raj.
            Agente: ¡Cuando quiera! ¿Hay algo más que pueda verificar por usted hoy?
            Cliente: No, eso es todo. ¡Gracias de nuevo!
            Agente: Gracias por llamarnos, Melissa. ¡Que tenga un buen día!"""
}

def run(lang: str):
    transcript = map[lang]
    cfg = CLMConfig(lang="es")
    encoder = CLMEncoder(cfg=cfg)
    print(encoder)
    new_result = encoder.encode(input_=transcript, metadata={})
    if new_result:
        print(f"  Compressed:  {new_result.compressed}")
        print("\nToken count (approximate):")
        print(f"  Original:  {new_result.n_tokens:>6} tokens")
        print(
            f"  Compressed:       {new_result.c_tokens:>6} tokens ({new_result.compression_ratio:.1f}% compression)"
        )

if __name__ == "__main__":
    run(lang="es")