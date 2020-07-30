Đồ Án: Tìm hiểu thư viện OpenCV và xây dựng chương trình chấm phiếu trắc nghiệm
'''

#Thêm thư viện tkinter thiết kế giao diện
from tkinter import *
from tkinter import filedialog
#Thêm thư viện pillow để đổi kích thước ảnh và chuyển sang định dạng ảnh của tkinter
from PIL import ImageTk, Image
#Thêm thư viện opencv để xử lý hình ảnh
import cv2
#Thêm thư viện numpy để xử lý tính toán
import numpy as np
#Thêm thư viện os để tương tác với hệ điều hành
import os

#Hàm mở file png/jpg
def openFile():
    #Mở cửa sổ chọn file, chỉ được chọn file có đuôi .png hoặc .jpg
    fileName = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("image files","*.png *.jpg"),("png files","*.png")))
    #Đọc ảnh từ file
    img = cv2.imread(fileName)
    #Chấm điểm
    scores(img)

#Hàm chấm điểm bằng camera
def openCamera():
    #Lấy danh sách đáp án
    listAnswerNumber = getAnswers()
    #Bắt đầu ghi hình từ camera, hiển thị trực tiếp
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    #Độ sáng ảnh
    cap.set(10,160)

    while True:
        success, img = cap.read()
        #Số báo danh
        myIDNumber = ""
        #Điểm
        score = -1
        #Thay đổi kích thước ảnh
        img = cv2.resize(img, (widthImg, heightImg))
        #Tạo ảnh đen khi chưa xử lý ảnh
        imgBlank = np.zeros_like(img)
        #Tạo ảnh chứa đường viền
        imgContours = img.copy()
        #Tạo ảnh hiển thị kết quả
        imgFinal = img.copy()
        #Tạo ảnh hiển thị các đường viền hình chữ nhật
        imgBiggestContours = img.copy()
        #Chuyển đổi hình ảnh sang không gian màu xám
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #Làm mờ hình ảnh bằng bộ lọc Gaussian
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
        #Tạo ảnh chứa các cạnh
        imgCanny = cv2.Canny(imgBlur, 10, 50)

        try:
            #Lấy ra danh sách các đường viền trong ảnh
            contours, hierachy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            #Vẽ các đường viền trong ảnh bằng màu xanh lá
            cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)
            #Tìm các đường viền hình chữ nhật
            rectCon = rectContour(contours)
            #4 điểm của ô số báo danh
            idNumber = getCornerPoints(rectCon[0])
            #4 điểm của ô đáp án
            biggestContour = getCornerPoints(rectCon[1])
            #4 điểm của ô điểm
            gradePoints = getCornerPoints(rectCon[2])
    
            if idNumber.size != 0 and biggestContour.size != 0 and gradePoints.size != 0:
                #Vẽ đường viền số báo danh theo BGR
                cv2.drawContours(imgBiggestContours, idNumber, -1, (0, 0, 255), 20)#first biggest red
                #Vẽ đường viền đáp án theo BGR
                cv2.drawContours(imgBiggestContours, biggestContour, -1, (0, 255, 0), 20)#second biggest green
                #Vẽ đường viền ô điểm theo BGR
                cv2.drawContours(imgBiggestContours, gradePoints, -1, (255, 0, 0), 20)#third biggest blue

                #Sắp xếp 4 góc theo thứ tự trái trên, góc phải trên, trái dưới, phải dưới
                idNumber = reorder(idNumber)
                biggestContour = reorder(biggestContour)
                gradePoints = reorder(gradePoints)

                #Đưa số báo danh lên một hình ảnh
                #Tọa độ 4 điểm gốc
                ptI1 = np.float32(idNumber)
                #Tọa độ 4 điểm sau khi chuyển đổi
                ptI2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
                #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
                matrixI = cv2.getPerspectiveTransform(ptI1, ptI2)
                #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
                imgIDDisplay = cv2.warpPerspective(img, matrixI, (widthImg, heightImg))
        
                #Đưa đáp án lên một hình ảnh
                #Tọa độ 4 điểm gốc
                pt1 = np.float32(biggestContour)
                #Tọa độ 4 điểm sau khi chuyển đổi
                pt2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
                #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
                matrix = cv2.getPerspectiveTransform(pt1, pt2)
                #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
                imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

                #Đưa điểm lên một hình ảnh
                #Tọa độ 4 điểm gốc
                ptG1 = np.float32(gradePoints)
                #Tọa độ 4 điểm sau khi chuyển đổi
                ptG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])
                #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
                matrixG = cv2.getPerspectiveTransform(ptG1, ptG2)
                #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
                imgGradeDisplay = cv2.warpPerspective(img, matrixG, (325, 150))
                #cv2.imshow("Grade", imgGradeDisplay)

                #Xử lý phần số báo danh
                #Chuyển ảnh đáp án về màu xám
                imgIDWarpGray = cv2.cvtColor(imgIDDisplay, cv2.COLOR_BGR2GRAY)
                #Chuyển đổi ảnh về đen trắng theo kiểu ngược lại đen thành trắng, trắng thành đen
                imgIDThresh = cv2.threshold(imgIDWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

                #Lưu trữ từng ô số báo danh
                boxesID = splitID(imgIDThresh)
                #Tạo biến lưu trữ giá trị pixel của mỗi ô
                myIDPixelValue = np.zeros((10, 6))
                countIDCol = 0
                countIDRow = 0
                #Tính số lượng pixel mỗi ô và lưu vào myPixelValue
                for imageID in boxesID:
                    totalIDPixel = cv2.countNonZero(imageID)
                    myIDPixelValue[countIDRow][countIDCol] = totalIDPixel
                    countIDCol +=1
                    if countIDCol == 6:
                        countIDRow +=1
                        countIDCol = 0
                #Tìm vị trí được tô
                myIDIndex = []
                for i in range(0, 6):
                    arr=[]
                    arr.clear()
                    for x in range(0, 10):
                        arr.append(myIDPixelValue[x][i])
                    myIndexValue = np.where(arr==np.amax(arr))
                    myIDIndex.append(myIndexValue[0][0])
                #Chuyển số báo danh sang dạng chuỗi
                myIDNumber = (''.join(map(str,myIDIndex)))
                #Kết thúc xử lý phần số báo danh
    
                #Xử lý phần đáp án
                #Chuyển ảnh đáp án về màu xám
                imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
                #Chuyển đổi ảnh về đen trắng theo kiểu ngược lại đen thành trắng, trắng thành đen
                imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

                #Lưu trữ từng ô đáp án
                boxes = splitBoxes(imgThresh)
                #Tạo biến lưu trữ giá trị pixel của mỗi ô
                myPixelValue = np.zeros((questions, choices))
                countCol = 0
                countRow = 0
    
                #Tính số lượng pixel mỗi ô và lưu vào myPixelValue
                for image in boxes:
                    totalPixel = cv2.countNonZero(image)
                    myPixelValue[countRow][countCol] = totalPixel
                    countCol +=1
                    if(countCol == choices):
                        countRow +=1
                        countCol = 0

                #Tìm vị trí được tô
                myIndex = []
                for x in range(0, questions):
                    arr = myPixelValue[x]
                    myIndexValue = np.where(arr==np.amax(arr))
                    myIndex.append(myIndexValue[0][0])
                #print (myIndex)

                #Lưu trữ các câu trả lời vào 1 mảng, nếu trả lời đúng thì giá trị ở câu đúng sẽ là 1, ngược lại là 0
                grading = []
                for x in range(0, questions):
                    if listAnswersNumber[x] == myIndex[x]:
                        grading.append(1)
                    else:
                        grading.append(0)

                #Tính điểm
                score = (sum(grading) / questions) * 10
                #Kết thúc xử lý phần đáp án

                #Hiển thị kết quả
                #Hiển thị hình ảnh số báo danh
                imgIDResult = imgIDDisplay.copy()
                showID(imgIDResult, myIDIndex, 10, 6)
                #Hiển thị hình ảnh xác định số báo danh, không hiển thị các ô
                imgRawID = np.zeros_like(imgIDDisplay)
                showID(imgRawID, myIDIndex, 10, 6)
                #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng
                invMatrixI = cv2.getPerspectiveTransform(ptI2, ptI1)
                #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh
                imgInvIDDisplay = cv2.warpPerspective(imgRawID, invMatrixI, (widthImg, heightImg))
                #Hiển thị hình ảnh đáp án sau khi được chấm
                imgResult = imgWarpColored.copy()
                showAnswers(imgResult, myIndex, grading, listAnswersNumber, questions, choices)
                #Hiển thị hình ảnh chấm điểm không hiển thị đáp án
                imgRawDrawing = np.zeros_like(imgWarpColored)
                showAnswers(imgRawDrawing, myIndex, grading, listAnswersNumber, questions, choices)
                #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng
                invMatrix = cv2.getPerspectiveTransform(pt2, pt1)
                #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh
                imgInvWrap = cv2.warpPerspective(imgRawDrawing, invMatrix, (widthImg, heightImg))
                #Hiển thị hình ảnh điểm không hiển thị ô điểm
                imgRawGrade = np.zeros_like(imgGradeDisplay)
                cv2.putText(imgRawGrade, str(int(score)), (120, 100), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 0, 255), 3)
                #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng
                invMatrixG = cv2.getPerspectiveTransform(ptG2, ptG1)
                #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh
                imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade, invMatrixG, (widthImg, heightImg))
                #Đưa ảnh số báo danh về hình bài thi
                imgFinal = cv2.addWeighted(imgFinal, 0.5, imgInvIDDisplay, 1, 0)
                #Đưa ảnh đáp án đã chấm điểm về hình bài thi
                imgFinal = cv2.addWeighted(imgFinal, 0.5, imgInvWrap, 1, 0)
                #Đưa ảnh điểm về hình bài thi
                imgFinal = cv2.addWeighted(imgFinal, 1, imgInvGradeDisplay, 1, 0)

                #hiển thị tất cả ảnh
                imgArray = ([img, imgCanny, imgContours, imgBiggestContours],
                    [imgIDThresh, imgThresh, imgResult, imgFinal])
        except:
            #Hiển thị ảnh đen nếu chưa xử lý
            imgArray = ([img, imgCanny, imgContours, imgBiggestContours],
                    [imgBlank, imgBlank, imgBlank, imgBlank])


        #Nhãn của mỗi ảnh
        labels = [["Original", "Canny", "Contours","Biggest Contour"],
        ["", "", "", "Final"]]
        #Sắp xếp thứ tự hiển thị các ảnh
        imgStacked = stackImages(imgArray, 0.5, labels)
        #Hiển thị ảnh
        cv2.imshow("Original", imgStacked)

        k = cv2.waitKey(1)
        #Nếu người dùng nhấn phím 's' thì sẽ lưu ảnh vào thư mục Scanned, lưu số báo danh và điểm vào file điểm
        if k == ord('s') or k == ord('S'):
            if myIDNumber != "" and score != -1:
                #Lưu số báo danh và điểm
                with open("DiemSo.txt", "a") as textFile:
                    textFile.write("IDNumber: " + myIDNumber + " , Grade: " + str(score) + "\n")
                #Lưu ảnh vào thư mục Scanned
                cv2.imwrite("Scanned/"+ myIDNumber +".png",imgFinal)
            #Hiển thị ảnh được lưu
            cv2.rectangle(imgStacked, ((int(imgStacked.shape[1] / 2) - 230), int(imgStacked.shape[0] / 2) + 50), (1100, 350), (0, 255, 0), cv2.FILLED)
            cv2.putText(imgStacked, "Scan Saved", (int(imgStacked.shape[1] / 2) - 200, int(imgStacked.shape[0] / 2)), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5, cv2.LINE_AA)
            cv2.imshow('Result', imgStacked)
            cv2.waitKey(1)
        #Nếu người dùng nhấn phím 'q' thì sẽ thoát khỏi chương trình chấm điểm bằng camera
        if k == ord('q') or k == ord ('Q'):
            cap.release()
            cv2.destroyAllWindows()
            break

#Hàm mở thư mục
def openDirectory():
    #Mở cửa sổ chọn thư mục
    folderName = filedialog.askdirectory()
    #Danh sách các ảnh có trong thư mục
    images = []
    for filename in os.listdir(folderName):
        #Đọc từng file
        img = cv2.imread(os.path.join(folderName,filename))
        #Nếu như là ảnh
        if img is not None:
            images.append(img)
    #Chấm điểm cho từng bài
    for i in images:
        scoresMultipleImage(i)
    #Sau khi chấm xong sẽ hiển thị file điểm
    os.system("start " + "DiemSo.txt")

#Hàm mở file đáp án
def openAnswers():
    os.system("start " + "DapAn.txt")

#Hàm mở file điểm
def openListGrade():
	os.system("start " + "DiemSo.txt")

#Hàm chấm điểm
def scores(img):
    #Lấy danh sách đáp án
    listAnswerNumber = getAnswers()
    #Thay đổi kích thước ảnh
    img = cv2.resize(img, (widthImg, heightImg))
    #Tạo ảnh đen khi chưa xử lý ảnh
    imgBlank = np.zeros_like(img)
    #Tạo ảnh chứa đường viền
    imgContours = img.copy()
    #Tạo ảnh hiển thị kết quả
    imgFinal = img.copy()
    #Tạo ảnh hiển thị các đường viền hình chữ nhật
    imgBiggestContours = img.copy()
    #Chuyển đổi hình ảnh sang không gian màu xám
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #Làm mờ hình ảnh bằng bộ lọc Gaussian
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    #Tạo ảnh chứa các cạnh
    imgCanny = cv2.Canny(imgBlur, 10, 50)

    try:
        #Lấy ra danh sách các đường viền trong ảnh
        contours, hierachy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #Vẽ các đường viền trong ảnh bằng màu xanh lá
        cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)
        #Tìm các đường viền hình chữ nhật
        rectCon = rectContour(contours)
        #4 điểm của ô số báo danh
        idNumber = getCornerPoints(rectCon[0])
        #4 điểm của ô đáp án
        biggestContour = getCornerPoints(rectCon[1])
        #4 điểm của ô điểm
        gradePoints = getCornerPoints(rectCon[2])
    
        if idNumber.size != 0 and biggestContour.size != 0 and gradePoints.size != 0:
            #Vẽ đường viền số báo danh theo BGR
            cv2.drawContours(imgBiggestContours, idNumber, -1, (0, 0, 255), 20)#first biggest red
            #Vẽ đường viền đáp án theo BGR
            cv2.drawContours(imgBiggestContours, biggestContour, -1, (0, 255, 0), 20)#second biggest green
            #Vẽ đường viền ô điểm theo BGR
            cv2.drawContours(imgBiggestContours, gradePoints, -1, (255, 0, 0), 20)#third biggest blue

            #Sắp xếp 4 góc theo thứ tự trái trên, góc phải trên, trái dưới, phải dưới
            idNumber = reorder(idNumber)
            biggestContour = reorder(biggestContour)
            gradePoints = reorder(gradePoints)

            #Đưa số báo danh lên một hình ảnh
            #Tọa độ 4 điểm gốc
            ptI1 = np.float32(idNumber)
            #Tọa độ 4 điểm sau khi chuyển đổi
            ptI2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
            #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
            matrixI = cv2.getPerspectiveTransform(ptI1, ptI2)
            #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
            imgIDDisplay = cv2.warpPerspective(img, matrixI, (widthImg, heightImg))
        
            #Đưa đáp án lên một hình ảnh
            #Tọa độ 4 điểm gốc
            pt1 = np.float32(biggestContour)
            #Tọa độ 4 điểm sau khi chuyển đổi
            pt2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
            #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
            matrix = cv2.getPerspectiveTransform(pt1, pt2)
            #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
            imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

            #Đưa điểm lên một hình ảnh
            #Tọa độ 4 điểm gốc
            ptG1 = np.float32(gradePoints)
            #Tọa độ 4 điểm sau khi chuyển đổi
            ptG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])
            #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
            matrixG = cv2.getPerspectiveTransform(ptG1, ptG2)
            #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
            imgGradeDisplay = cv2.warpPerspective(img, matrixG, (325, 150))

            #Xử lý phần số báo danh
            #Chuyển ảnh đáp án về màu xám
            imgIDWarpGray = cv2.cvtColor(imgIDDisplay, cv2.COLOR_BGR2GRAY)
            #Chuyển đổi ảnh về đen trắng theo kiểu ngược lại đen thành trắng, trắng thành đen
            imgIDThresh = cv2.threshold(imgIDWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

            #Lưu trữ từng ô số báo danh
            boxesID = splitID(imgIDThresh)
            #Tạo biến lưu trữ giá trị pixel của mỗi ô
            myIDPixelValue = np.zeros((10, 6))
            countIDCol = 0
            countIDRow = 0
            #Tính số lượng pixel mỗi ô và lưu vào myPixelValue
            for imageID in boxesID:
                totalIDPixel = cv2.countNonZero(imageID)
                myIDPixelValue[countIDRow][countIDCol] = totalIDPixel
                countIDCol +=1
                if countIDCol == 6:
                    countIDRow +=1
                    countIDCol = 0
            #print(myIDPixelValue)
            #Tìm vị trí được tô
            myIDIndex = []
            for i in range(0, 6):
                arr=[]
                arr.clear()
                for x in range(0, 10):
                    arr.append(myIDPixelValue[x][i])
                myIndexValue = np.where(arr==np.amax(arr))
                myIDIndex.append(myIndexValue[0][0])
            #Chuyển số báo danh sang dạng chuỗi
            myIDNumber = (''.join(map(str,myIDIndex)))
            #Kết thúc xử lý phần số báo danh

            #Xử lý phần đáp án
            #Chuyển ảnh đáp án về màu xám
            imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
            #Chuyển đổi ảnh về đen trắng theo kiểu ngược lại đen thành trắng, trắng thành đen
            imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

            #Lưu trữ từng ô đáp án
            boxes = splitBoxes(imgThresh)
            #Tạo biến lưu trữ giá trị pixel của mỗi ô
            myPixelValue = np.zeros((questions, choices))
            countCol = 0
            countRow = 0

            #Tính số lượng pixel mỗi ô và lưu vào myPixelValue
            for image in boxes:
                totalPixel = cv2.countNonZero(image)
                myPixelValue[countRow][countCol] = totalPixel
                countCol +=1
                if(countCol == choices):
                    countRow +=1
                    countCol = 0

            #Tìm vị trí được tô
            myIndex = []
            for x in range(0, questions):
                arr = myPixelValue[x]
                myIndexValue = np.where(arr==np.amax(arr))
                myIndex.append(myIndexValue[0][0])

            #Lưu trữ các câu trả lời vào 1 mảng, nếu trả lời đúng thì giá trị ở câu đúng sẽ là 1, ngược lại là 0
            grading = []
            for x in range(0, questions):
                if listAnswersNumber[x] == myIndex[x]:
                    grading.append(1)
                else:
                    grading.append(0)

            #Tính điểm
            score = (sum(grading) / questions) * 10

            #Lưu số báo danh và điểm ra file điểm
            with open("DiemSo.txt", "a") as textFile:
                textFile.write("IDNumber: " + myIDNumber + " , Grade: " + str(score) + "\n")

            #Kết thúc xử lý phần đáp án

            #Hiển thị kết quả
            #Hiển thị hình ảnh số báo danh
            imgIDResult = imgIDDisplay.copy()
            showID(imgIDResult, myIDIndex, 10, 6)
            #Hiển thị hình ảnh xác định số báo danh, không hiển thị các ô
            imgRawID = np.zeros_like(imgIDDisplay)
            showID(imgRawID, myIDIndex, 10, 6)
            #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng
            invMatrixI = cv2.getPerspectiveTransform(ptI2, ptI1)
            #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh
            imgInvIDDisplay = cv2.warpPerspective(imgRawID, invMatrixI, (widthImg, heightImg))
            #Hiển thị hình ảnh đáp án sau khi được chấm
            imgResult = imgWarpColored.copy()
            showAnswers(imgResult, myIndex, grading, listAnswersNumber, questions, choices)
            #Hiển thị hình ảnh chấm điểm không hiển thị đáp án
            imgRawDrawing = np.zeros_like(imgWarpColored)
            showAnswers(imgRawDrawing, myIndex, grading, listAnswersNumber, questions, choices)
            #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng
            invMatrix = cv2.getPerspectiveTransform(pt2, pt1)
            #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh
            imgInvWrap = cv2.warpPerspective(imgRawDrawing, invMatrix, (widthImg, heightImg))
            #Hiển thị hình ảnh điểm không hiển thị ô điểm
            imgRawGrade = np.zeros_like(imgGradeDisplay)
            cv2.putText(imgRawGrade, str(int(score)), (120, 100), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 0, 255), 3)
            #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng
            invMatrixG = cv2.getPerspectiveTransform(ptG2, ptG1)
            #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh
            imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade, invMatrixG, (widthImg, heightImg))
            #Đưa ảnh số báo danh về hình bài thi
            imgFinal = cv2.addWeighted(imgFinal, 0.5, imgInvIDDisplay, 1, 0)
            #Đưa ảnh đáp án đã chấm điểm về hình bài thi
            imgFinal = cv2.addWeighted(imgFinal, 0.5, imgInvWrap, 1, 0)
            #Đưa ảnh điểm về hình bài thi
            imgFinal = cv2.addWeighted(imgFinal, 1, imgInvGradeDisplay, 1, 0)
            #Hiển thị tất cả ảnh
            imgArray = ([img, imgCanny, imgContours, imgBiggestContours],
                [imgIDThresh, imgThresh, imgResult, imgFinal])
    except:
        #Hiển thị ảnh đen nếu chưa xử lý
        imgArray = ([img, imgCanny, imgContours, imgBiggestContours],
                [imgBlank, imgBlank, imgBlank, imgBlank])


    #Nhãn của mỗi ảnh
    labels = [["Original", "Canny", "Contours","Biggest Contour"],
    ["", "", "", "Final"]]
    #Sắp xếp thứ tự hiển thị của các ảnh
    imgStacked = stackImages(imgArray, 0.5, labels)
    #Hiển thị ảnh
    cv2.imshow("Original", imgStacked)

#Hàm chấm điểm nhiều bài
def scoresMultipleImage(img):
    #Lấy danh sách đáp án
    listAnswerNumber = getAnswers()
    #Thay đổi kích thước ảnh
    img = cv2.resize(img, (widthImg, heightImg))
    #Tạo ảnh đen khi chưa xử lý ảnh
    imgBlank = np.zeros_like(img)
    #Tạo ảnh chứa đường viền
    imgContours = img.copy()
    #Tạo ảnh hiển thị kết quả
    imgFinal = img.copy()
    #Tạo ảnh hiển thị các đường viền hình chữ nhật
    imgBiggestContours = img.copy()
    #Chuyển đổi hình ảnh sang không gian màu xám
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #Làm mờ hình ảnh bằng bộ lọc Gaussian
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    #Tạo ảnh chứa các cạnh
    imgCanny = cv2.Canny(imgBlur, 10, 50)

    #Lấy ra danh sách các đường viền trong ảnh
    contours, hierachy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #Vẽ các đường viền trong ảnh bằng màu xanh lá
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)
    #Tìm các đường viền hình chữ nhật
    rectCon = rectContour(contours)
    #4 điểm của ô số báo danh
    idNumber = getCornerPoints(rectCon[0])
    #4 điểm của ô đáp án
    biggestContour = getCornerPoints(rectCon[1])
    #4 điểm của ô điểm
    gradePoints = getCornerPoints(rectCon[2])

    if idNumber.size != 0 and biggestContour.size != 0 and gradePoints.size != 0:
        #Vẽ đường viền số báo danh theo BGR
        cv2.drawContours(imgBiggestContours, idNumber, -1, (0, 0, 255), 20)#first biggest red
        #Vẽ đường viền đáp án theo BGR
        cv2.drawContours(imgBiggestContours, biggestContour, -1, (0, 255, 0), 20)#second biggest green
        #Vẽ đường viền ô điểm theo BGR
        cv2.drawContours(imgBiggestContours, gradePoints, -1, (255, 0, 0), 20)#third biggest blue

        #Sắp xếp 4 góc theo thứ tự trái trên, góc phải trên, trái dưới, phải dưới
        idNumber = reorder(idNumber)
        biggestContour = reorder(biggestContour)
        gradePoints = reorder(gradePoints)

        #Đưa số báo danh lên một hình ảnh
        #Tọa độ 4 điểm gốc
        ptI1 = np.float32(idNumber)
        #Tọa độ 4 điểm sau khi chuyển đổi
        ptI2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
        matrixI = cv2.getPerspectiveTransform(ptI1, ptI2)
        #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
        imgIDDisplay = cv2.warpPerspective(img, matrixI, (widthImg, heightImg))
    
        #Đưa đáp án lên một hình ảnh
        #Tọa độ 4 điểm gốc
        pt1 = np.float32(biggestContour)
        #Tọa độ 4 điểm sau khi chuyển đổi
        pt2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
        matrix = cv2.getPerspectiveTransform(pt1, pt2)
        #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        #Đưa điểm lên một hình ảnh
        #Tọa độ 4 điểm gốc
        ptG1 = np.float32(gradePoints)
        #Tọa độ 4 điểm sau khi chuyển đổi
        ptG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])
        #Tính toán một biến đổi phối cảnh từ bốn cặp điểm tương ứng.
        matrixG = cv2.getPerspectiveTransform(ptG1, ptG2)
        #Áp dụng một chuyển đổi phối cảnh cho một hình ảnh.
        imgGradeDisplay = cv2.warpPerspective(img, matrixG, (325, 150))

        #Xử lý phần số báo danh
        #Chuyển ảnh đáp án về màu xám
        imgIDWarpGray = cv2.cvtColor(imgIDDisplay, cv2.COLOR_BGR2GRAY)
        #Chuyển đổi ảnh về đen trắng theo kiểu ngược lại đen thành trắng, trắng thành đen
        imgIDThresh = cv2.threshold(imgIDWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

        #Lưu trữ từng ô số báo danh
        boxesID = splitID(imgIDThresh)
        #Tạo biến lưu trữ giá trị pixel của mỗi ô
        myIDPixelValue = np.zeros((10, 6))
        countIDCol = 0
        countIDRow = 0
        #Tính số lượng pixel mỗi ô và lưu vào myPixelValue
        for imageID in boxesID:
            totalIDPixel = cv2.countNonZero(imageID)
            myIDPixelValue[countIDRow][countIDCol] = totalIDPixel
            countIDCol +=1
            if countIDCol == 6:
                countIDRow +=1
                countIDCol = 0
        #print(myIDPixelValue)
        #Tìm vị trí được tô
        myIDIndex = []
        for i in range(0, 6):
            arr=[]
            arr.clear()
            for x in range(0, 10):
                arr.append(myIDPixelValue[x][i])
            myIndexValue = np.where(arr==np.amax(arr))
            myIDIndex.append(myIndexValue[0][0])
        #Chuyển số báo danh sang dạng chuỗi
        myIDNumber = (''.join(map(str,myIDIndex)))
        #Kết thúc xử lý phần số báo danh

        #Xử lý phần đáp án
        #Chuyển ảnh đáp án về màu xám
        imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        #Chuyển đổi ảnh về đen trắng theo kiểu ngược lại đen thành trắng, trắng thành đen
        imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

        #Lưu trữ từng ô đáp án
        boxes = splitBoxes(imgThresh)
        #Tạo biến lưu trữ giá trị pixel của mỗi ô
        myPixelValue = np.zeros((questions, choices))
        countCol = 0
        countRow = 0

        #Tính số lượng pixel mỗi ô và lưu vào myPixelValue
        for image in boxes:
            totalPixel = cv2.countNonZero(image)
            myPixelValue[countRow][countCol] = totalPixel
            countCol +=1
            if(countCol == choices):
                countRow +=1
                countCol = 0

        #Tìm vị trí được tô
        myIndex = []
        for x in range(0, questions):
            arr = myPixelValue[x]
            myIndexValue = np.where(arr==np.amax(arr))
            myIndex.append(myIndexValue[0][0])

        #Lưu trữ các câu trả lời vào 1 mảng, nếu trả lời đúng thì giá trị ở câu đúng sẽ là 1, ngược lại là 0
        grading = []
        for x in range(0, questions):
            if listAnswersNumber[x] == myIndex[x]:
                grading.append(1)
            else:
                grading.append(0)

        #Tính điểm
        score = (sum(grading) / questions) * 10

        #Lưu số báo danh và điểm ra file điểm
        with open("DiemSo.txt", "a") as textFile:
            textFile.write("IDNumber: " + myIDNumber + " , Grade: " + str(score) + "\n")
        #Kết thúc xử lý phần đáp án

#Hàm lấy đáp án
def getAnswers():
    #Mở file đáp án
    myFile = open("DapAn.txt", "r")
    #Đọc từng hàng file đáp án
    listAnswersWord = myFile.read().splitlines()
    print (listAnswersWord)
    myFile.close()
    #Danh sách chứa số tương ứng với đáp án
    listAnswersNumber.clear()
    for i in listAnswersWord:
        temp = i.split(".")
        if temp[1] == "A":
            listAnswersNumber.append(0)
        elif temp[1] == "B":
            listAnswersNumber.append(1)
        elif temp[1] == "C":
            listAnswersNumber.append(2)
        elif temp[1] == "D":
            listAnswersNumber.append(3)
        elif temp[1] == "E":
            listAnswersNumber.append(4)
    return listAnswersNumber

#Sắp xếp các hình ảnh hiển thị
def stackImages(imgArray,scale,labels=[]):
    #Số hàng hiển thị
    rows = len(imgArray)
    #Số cột hiển thị
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range (0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        print ("Not Available")
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        hor_con= np.concatenate(imgArray)
        ver = hor
    if len(labels) != 0:
        eachImgWidth= int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        for d in range(0, rows):
            for c in range (0,cols):
                if labels[d][c] != "":
                    cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(labels[d][c])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                    cv2.putText(ver,labels[d][c],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)
    return ver

#Sắp xếp lại vị trí của 4 điểm trái trên, phải trên, trái dưới, phải dưới
def reorder(myPoints):
	#Cung cấp hình dạng mới gồm 4 hàng 2 cột
    myPoints = myPoints.reshape((4, 2))
    #Tạo ra một ma trận các phần tử 0 gồm 4 mảng chứa 1 hàng có 2 phần tử
    myPointsNew = np.zeros((4, 1, 2), np.int32)
    #Tính tổng từng hàng
    add = myPoints.sum(1)
    #Trả về vị trí của số nhỏ nhất trong mảng tổng
    myPointsNew[0] = myPoints[np.argmin(add)]  #[0,0]
    #Trả về vị trí của số lớn nhất trong mảng tổng
    myPointsNew[3] = myPoints[np.argmax(add)]   #[w,h]
    #Tính hiệu từng hàng trong mảng ban đầu
    diff = np.diff(myPoints, axis=1)
    #Trả về vị trí của số nhỏ nhất trong mảng hiệu
    myPointsNew[1] = myPoints[np.argmin(diff)]  #[w,0]
    #Trả về vị trí của số nhỏ nhất trong mảng hiệu
    myPointsNew[2] = myPoints[np.argmax(diff)] #[h,0]
    #Trả về danh sách tọa độ 4 điểm trái trên, phải trên, trái dưới, phải dưới
    return myPointsNew

#Lấy các hình chữ nhật trong ảnh
def rectContour(contours):
    #Danh sách các hình chữ nhật
    rectCon = []
    for i in contours:
        #Tính diện tích hình của đường viền
        area = cv2.contourArea(i)
        #Chỉ xét các hình của đường viền có diện tích lớn hơn 50
        if area > 50:
            #Tính chu vi đường viền kín
            peri = cv2.arcLength(i, True)
            #Tính xấp xỉ đường viền với một đa giác kín, độ chính xác bằng 2% của chu vi
            #nghĩa là khoảng cách lớn nhất giữa đường viền và xấp xỉ phải nhỏ hơn 2% chu vi
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            #Tìm các đa giác có 4 điểm (hình chữ nhật)
            if len(approx) == 4:
                rectCon.append(i)
    #Sắp xếp danh sách các hình chữ nhật theo diện tích giảm dần
    rectCon = sorted(rectCon, key=cv2.contourArea,reverse=True)
    #Trả về danh sách hình chữ nhật
    return rectCon

#Lấy ra 4 điểm của hình chữ nhật
def getCornerPoints(cont):
    #Tính chu vi đường viền kín
    peri = cv2.arcLength(cont, True)
    #Tính xấp xỉ đường viền với một đa giác kín, độ chính xác bằng 2% của chu vi
    #nghĩa là khoảng cách lớn nhất giữa đường viền và xấp xỉ phải nhỏ hơn 2% chu vi
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
    #Trả về 4 điểm
    return approx

#Chia các ô đáp án
def splitBoxes(img):
    #Chia ảnh ra thành từng hàng
    rows = np.vsplit(img,5)
    #Danh sách các ô
    boxes=[]
    for r in rows:
        #Chia hàng ra thành từng ô theo cột
        cols = np.hsplit(r,5)
        for box in cols:
            boxes.append(box)
    #Trả về danh sách các ô
    return boxes

#Chia các ô số báo danh
def splitID(img):
    #Chia ảnh ra thành từng hàng
    rows = np.vsplit(img, 10)
    #cv2.imshow("Cell", rows[0])
    #Danh sách các ô
    boxes=[]
    for r in rows:
        #Chia hàng ra thành từng ô theo cột
        cols = np.hsplit(r, 6)
        #cv2.imshow("Cell", cols[5])
        for box in cols:
            boxes.append(box)
    #Trả về danh sách các ô
    return boxes

#Hiển thị điểm lên ảnh
def showAnswers(img,myIndex,grading,ans,questions=5,choices=5):
    #Độ rộng của mỗi ô đáp án
    secW = int(img.shape[1]/choices)
    #Độ dài của mỗi ô đáp án
    secH = int(img.shape[0]/questions)

    for x in range(0,questions):
        #Vị trí của từng ô đáp án
        myAns= myIndex[x]
        #Tìm tâm của đáp án
        cX = (myAns * secW) + secW // 2
        cY = (x * secH) + secH // 2
        #Nếu đúng thì tô màu xanh lá
        if grading[x]==1:
            myColor = (0,255,0)
            cv2.circle(img,(cX,cY),50,myColor,cv2.FILLED)
        #Nếu sai thì tô màu đỏ
        else:
            myColor = (0,0,255)
            cv2.circle(img, (cX, cY), 50, myColor, cv2.FILLED)
            #Tô đáp án chính xác
            myColor = (0, 255, 0)
            #Vị trí của đáp án chính xác
            correctAns = ans[x]
            cv2.circle(img,((correctAns * secW)+secW//2, (x * secH)+secH//2),
            20,myColor,cv2.FILLED)

#Hiển thị số báo danh lên ảnh
def showID(img, myIDIndex, rows, cols):
    #Độ rộng của mỗi ô số báo danh
    secW = int(img.shape[1]/cols)
    #Độ dài của mỗi ô số báo danh
    secH = int(img.shape[0]/rows)
    #print (secW, secH)
    for x in range(0, 6):
        #Vị trí từng số trong số báo danh theo cột
        myID = myIDIndex[x]
        #Tìm tâm của số
        cX = (x * secW) + secW // 2
        cY = (myID * secH) + secH //2
        #Màu xanh BGR
        myColor = (255, 0, 0)
        #Vẽ hình tròn ở ô số báo danh
        cv2.circle(img, (cX, cY), 25, myColor, cv2.FILLED)

#Độ rộng của ảnh
widthImg = 600
#Độ dài của ảnh
heightImg = 600
#Số câu hỏi
questions = 5
#Số câu trả lời
choices = 5
#Danh sách đáp án
listAnswersNumber = []

#Tạo đối tượng window
window = Tk()
#Title
window.title("Chương trình chấm phiếu điểm trắc nghiệm")
#Phóng to màn hình
window.state('zoomed')
#Không cho thay đổi kích thước cửa sổ
window.resizable(False, False)

#Chia màn hình ra thành 6 hàng và 5 cột
for i in range(6):
    window.rowconfigure(i, weight=1)
for i in range(5):
    window.columnconfigure(i, weight=1)

#Tạo canvas chứa ảnh và mô tả
canvas = Canvas(window)
canvas.grid(row=0, column=2, rowspan=6, columnspan=2,sticky="nsew")
#Lấy ảnh
img = Image.open("TemplateID.png")
#Chỉnh sửa kích thước ảnh
img = img.resize((680, 700), Image.ANTIALIAS)
#Chuyển ảnh về định dạng ảnh Tkinter
image = ImageTk.PhotoImage(img)

#Tạo ảnh trên canvas
canvas.create_image(0, 0, image=image, anchor=NW)
#Tạo mô tả trên canvas
canvas.create_text(250, 710, font=(25), fill='red', text="Mẫu phiếu trắc nghiệm", anchor=NW)

#Nút chấm 1 bài
b1 = Button(window, text="Chấm 1 bài", command=openFile)
b1.grid(row=1, column=4,rowspan=2, columnspan=2, sticky="n")
#Nút chấm bài bằng camera
b2 = Button(window, text="Chấm bài \n bằng camera", command=openCamera)
b2.grid(row=2, column=4,rowspan=2, columnspan=2, sticky="n")
#Nút chấm nhiều bài
b3 = Button(window, text="Chấm nhiều bài \n trong thư mục", command=openDirectory)
b3.grid(row=3, column=4,rowspan=2, columnspan=2, sticky="n")
#Nút xem điểm các bài đã chấm
b4 = Button(window, text="Xem điểm", command=openListGrade)
b4.grid(row=4, column=4,rowspan=2, columnspan=2, sticky="n")
#Nút xem file đáp án
b5 = Button(window, text="Xem đáp án", command=openAnswers)
b5.grid(row=5, column=4,rowspan=2, columnspan=2, sticky="n")

window.mainloop()