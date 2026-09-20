"""Mock-mode integration tests. Never call OpenAI or charge real money."""
import io,json,os,tempfile,time,unittest,sys
from pathlib import Path
os.environ['DATA_DIR']=tempfile.mkdtemp(prefix='thread-test-')
os.environ['GENERATION_MODE']='mock'
os.environ['COOKIE_SECURE']='false'
os.environ['ALLOWED_ORIGINS']='http://testserver'
os.environ['FREE_DAILY_LIMIT']='20'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from PIL import Image
from app import app,db,password_hash,verify_password

class Integration(unittest.TestCase):
    def test_whole_flow(self):
        origin={'Origin':'http://testserver'}
        image=io.BytesIO();Image.new('RGB',(500,600),'navy').save(image,'JPEG');photo=image.getvalue()
        with TestClient(app) as seller:
            self.assertTrue(seller.get('/api/health').json()['ok'])
            denied=seller.post('/api/auth/signup',json={'email':'a@b.com','name':'demo','password':'safe-password','role':'seller'})
            self.assertEqual(denied.status_code,403)
            user=seller.post('/api/auth/signup',headers=origin,json={'email':'seller@example.com','name':'샘플 판매자','password':'correct-password','role':'seller'})
            self.assertEqual(user.status_code,200,user.text)
            self.assertNotIn('password',user.json()['user'])
            self.assertEqual(seller.get('/api/jobs').status_code,403)
            user_id=user.json()['user']['id']
            with db() as c:c.execute('UPDATE users SET approved=1 WHERE id=?',(user_id,))
            product={'name':'<script>상품</script>','category':'상의','material':'면 100%','sizes':'S, M','colors':'네이비','origin':'대한민국','notes':'원본 확인'}
            def submit(plan='free',consent='true'):
                return seller.post('/api/generate',headers=origin,data={'product':json.dumps(product),'plan':plan,'publishConsent':consent},files={'front':('front.jpg',photo,'image/jpeg'),'detail':('detail.jpg',photo,'image/jpeg')})
            self.assertEqual(submit(consent='false').status_code,422)
            self.assertEqual(submit(plan='paid').status_code,402)
            created=submit();self.assertEqual(created.status_code,202,created.text);job=created.json()['jobId']
            for _ in range(100):
                output=seller.get('/api/jobs/'+job).json()
                if output['status'] not in ('queued','processing'):break
                time.sleep(.02)
            self.assertEqual(output['status'],'completed',output)
            self.assertTrue(output['mock']);self.assertFalse(output['imageGenerated'])
            self.assertEqual(len(output['images']),2)
            image_url=output['images'][0]['url']
            self.assertEqual(seller.get(image_url).status_code,200)
            # Another authenticated seller cannot access job metadata or images.
            old_cookie=seller.cookies.get('thread_session');seller.cookies.clear()
            other=seller.post('/api/auth/signup',headers=origin,json={'email':'other@example.com','name':'다른판매자','password':'correct-password','role':'seller'}).json()['user']
            with db() as c:c.execute('UPDATE users SET approved=1 WHERE id=?',(other['id'],))
            self.assertEqual(seller.get('/api/jobs/'+job).status_code,404)
            self.assertEqual(seller.get(image_url).status_code,404)
            seller.cookies.clear();seller.cookies.set('thread_session',old_cookie)
            download=seller.post('/api/jobs/'+job+'/download',headers=origin)
            self.assertEqual(download.status_code,200,download.text[:100])
            self.assertIn('&lt;script&gt;',download.text);self.assertNotIn('<script>상품',download.text)
            self.assertIn('data:image/jpeg;base64,',download.text)
            self.assertEqual(seller.post('/api/jobs/'+job+'/download',headers=origin).status_code,403)
            self.assertEqual(seller.get('/api/jobs/'+job).json()['downloadsRemaining'],0)
            published=seller.post('/api/jobs/'+job+'/publish',headers=origin,json={'price':39000,'stock':8,'reviewed':True})
            self.assertEqual(published.status_code,200,published.text);p=published.json()['product']
            self.assertEqual(seller.post('/api/jobs/'+job+'/publish',headers=origin,json={'price':39000,'stock':8,'reviewed':True}).json()['product']['id'],p['id'])
            seller.cookies.clear()
            self.assertEqual(seller.get(p['image']).status_code,200)
            self.assertEqual(len(seller.get('/api/products').json()['products']),1)
            self.assertEqual(seller.get(image_url).status_code,401)
            customer=seller.post('/api/auth/signup',headers=origin,json={'email':'buyer@example.com','name':'구매자','password':'correct-password','role':'customer'})
            self.assertEqual(customer.status_code,200)
            items=[{'id':p['id'],'color':'네이비','size':'S','quantity':2}]
            quote=seller.post('/api/checkout/quote',headers=origin,json={'items':items})
            self.assertEqual(quote.status_code,200,quote.text);self.assertEqual(quote.json()['total'],81000);self.assertFalse(quote.json()['checkoutEnabled'])
            self.assertEqual(seller.post('/api/orders',headers=origin,json={}).status_code,503)
            self.assertEqual(seller.get('/api/jobs').status_code,403)
            self.assertEqual(seller.post('/api/checkout/quote',headers=origin,json={'items':items*5}).status_code,409)
            self.assertEqual(seller.post('/api/auth/logout',headers=origin).status_code,200)
            self.assertEqual(seller.get('/api/auth/me').status_code,401)
            self.assertEqual(seller.post('/api/auth/login',headers=origin,json={'email':'buyer@example.com','password':'wrong'}).status_code,401)
            self.assertEqual(seller.post('/api/auth/login',headers=origin,json={'email':'buyer@example.com','password':'correct-password'}).status_code,200)
            self.assertTrue(verify_password('  preserved spaces  ',password_hash('  preserved spaces  ')))
if __name__=='__main__':unittest.main()
