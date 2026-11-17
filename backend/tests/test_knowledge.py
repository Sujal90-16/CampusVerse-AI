from app.services.knowledge import chunks
def test_chunks_overlap_and_content():
 parts=chunks('alpha '*500,size=100,overlap=20)
 assert len(parts)>1 and all(parts)
