def encode_firework(model):
    return {
        'location': model.location,
        'sponsor': model.sponsor,
        'event_at': model.event_at.isoformat(),
        'updated_at': model.updated_at.isoformat(),
        'created_at': model.created_at.isoformat()
    }
