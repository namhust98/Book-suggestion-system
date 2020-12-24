"""
config.py

File khoi chay chuong trinh
"""

from load_data import Database
from lsh import LSH
import config
import metrics
import time

model_base = Database()
model_lsh = LSH(config.NUM_HASH_FUNCTIONS, config.NUM_BLOCKS, config.BLOCK_SIZE, \
					config.NUM_NEAREST_NEIGHBORS, model_base.set_of_user)
def create_clusters():
	print("Dang load du lieu tu file...")
	model_base.load_data_from_ratings_file()
	model_base.load_data_from_books_file()
	print("Da load du lieu xong, bat dau thuc hien phan cum items...")
	t1 = time.time()
	model_lsh.pick_family_MIH_functions()
	#model_base.num_items = 1000
	for item_id in range(model_base.num_items):
		model_lsh.locality_senstive_hashing(item_id)
	elapsed1 = (time.time() - t1)
	print("Da phan cum xong!")
	return elapsed1


def get_recommended_books(item_id):
	result = []
	if item_id in model_lsh.similarity:
		items_list = model_lsh.similarity[item_id]
	else:
		model_lsh.find_similarity_items(item_id)
		items_list = model_lsh.similarity[item_id]
	for i in items_list:
		result.append(model_base.book_titles_list[i])
	return result

def name_input():
	print("Nhap ten sach de tim kiem: ")
	name = input()
	name = name.lower()
	matching = model_base.find_name_of_book(name)
	if len(matching) == 0:
		print("Khong tim thay ten sach nao phu hop")
	else:
		print("Chon id phu hop voi ten sach: ")
		for i in matching:
			print(model_base.book_titles_list[i] + " -- " + "id: " + str(i))

def id_input():
	check = 0
	print("Nhap id cua cac sach (cach nhau boi khoang trang (space), nhan enter de ket thuc viec nhap): ")
	items = input()
	for character in items:
		if character.isalpha():
			print("Nhap sai, moi nhap lai")
			check = 1
			break
	if check == 0:
		items = [int(x.strip()) for x in items.split()]
		return items
	else:
		return []
	

def get_items_id_list():
	items_id_list = []
	while True:
		print("Nhap 1 de nhap id cua sach, 2 de nhap ten sach, 3 de ket thuc viec nhap")
		ch = input()
		if ch == '1':
			items_id_list += id_input()
			items_id_list = list(set(items_id_list))
		elif ch == '2':
			name_input()
			items_id_list += id_input()
			items_id_list = list(set(items_id_list))
		elif ch == '3':
			break
		else:
			print("Nhap sai, vui long nhap lai")
	return items_id_list

def main():
	print("\n ****HE THONG GOI Y SACH**** \n" + "="*35 + '\n\n')
	# t1 = time.time()
	elapsed1 = create_clusters()
	# elapsed1 = (time.time() - t1)
	# print "\nThoi gian phan cum items: %.2fsec" % elapsed1
	# del t1, elapsed1
	while True:
		print("Nhap tuy chon: \n")
		print("1. Goi y sach")
		print("2. Them sach moi vao co so du lieu")
		print("3. Cap nhat cac user thich sach")
		print("4. Top 10 quyen sach duoc danh gia cao nhat")
		print("5. Top 10 quyen sach pho bien chon nhat")
		print("6. Thong ke chuong trinh")
		print("7. Ket thuc chuong trinh")
		ch = input()
		if ch == '1':
			print("\n ****Goi y sach**** \n" + "="*35 + '\n')
			items_id_list = get_items_id_list()
			# print items_id_list
			if len(items_id_list) == 0:
				print("Chua nhap cac cuon sach ma ban thich")
			else:
				print("Cac sach ma ban thich: \n")
				liked_book = []
				for i in items_id_list:
					print(model_base.book_titles_list[i])
					liked_book.append(model_base.book_titles_list[i])
				result = []
				for i in items_id_list:
					result += get_recommended_books(i)
				result = list(set(result)) #remove duplicate
				for i in liked_book:
					if i in result: result.remove(i)
				print("\n Cac sach ma ban nen doc: \n")
				for i in result:
					print(i)

		elif ch == '2':
			print("\n ****Them sach moi**** \n" + "="*35 + '\n')
			new_item_id = model_base.add_item()
			model_lsh.locality_senstive_hashing(new_item_id) # bam user moi vao cum

		elif ch == '3':
			print("\n ****Cap nhat user thich sach**** \n" + "="*35 + '\n')
			items_update = get_items_id_list()
			for i in items_update:
				print("Cap nhat cho sach: ", model_base.book_titles_list[i])
				model_base.update_item_rates(i)
				model_lsh.remove_item_from_clusters(i) # xoa item dang xet ra khoi tat ca cac cum
				model_lsh.locality_senstive_hashing(i) # bam lai item vao cac cum
			print("\n Da cap nhat xong! \n")

		elif ch == '4':
			print("\n ****Top 10 quyen sach duoc danh gia cao nhat**** \n" + "="*35 + '\n')
			for i in model_base.top_rated_books:
				print(i[0])

		elif ch == '5':
			print("\n ****Top 10 quyen sach pho bien nhat**** \n" + "="*35 + '\n')
			for i in model_base.top_popular_books:
				print(i[0])

		elif ch == '6':
			print("\n ****Thong ke chuong trinh**** \n" + "="*35 + '\n')
			print("\nThoi gian phan cum items: %.2fsec" % elapsed1)
			t = time.time()
			model_lsh.find_all_similarity()		#set_of_user
			elapsed = (time.time() - t)
			print("\nThoi gian tim cac items tuong dong giua tren phuong phap LSH: %.2fsec" % elapsed)
			del t, elapsed
			true = metrics.jaccard_calc(model_base.num_items, model_base.set_of_user)
			# print model_lsh.similarity[0]
			# print true[0]
			print("Do chinh xac: ", metrics.accuracy_calc(model_lsh.similarity, true, model_base.num_items))

		elif ch == '7':
			break
		else:
			print("Nhap sai, vui long nhap lai")


if __name__ == '__main__':	
	main()