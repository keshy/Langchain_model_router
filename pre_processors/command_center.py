def contextualize(**kwargs):
    prisma_id = kwargs.get('prismaId')
    return """
        Today we found a lot of issues in this customer environment with 100s of alerts and thousands of vulnerabilities!
    """
